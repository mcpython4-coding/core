"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import typing
import copy
from abc import ABC

import mcpython.common.event.Registry
from mcpython import logger
from mcpython import shared


class FactoryBuilder:
    """
    This system is for building classes for building other classes.
    It contains base classes for creating custom class-builder segments
    and default classes for them.

    You can do nearly anything with it what you want
    Performance-wise this is no critical section as it is only called during launch.
    Only critical is the IFactoryClassBuilder class modifying the target class of the builder,
    which is than send to the system
    """

    class IFactoryClassModifier(ABC):
        @classmethod
        def apply(
            cls,
            builder: "FactoryBuilder",
            target: typing.Type["FactoryBuilder.IFactory"],
        ) -> typing.Type["FactoryBuilder.IFactory"]:
            raise NotImplementedError()

    class IFactoryConfigurator(ABC):
        def __init__(self, config_name: str):
            self.config_name = config_name

        def prepare(self, instance: "FactoryBuilder.IFactory"):
            pass

        def get_configurable_target(self) -> typing.Any:
            raise NotImplementedError()

    class InnerDefaultAttributeHelper(IFactoryConfigurator):
        def __init__(self, name: str, attr_name: str, value: typing.Callable):
            super().__init__(name)
            self.attr_name = attr_name
            self.value = value

        def prepare(self, instance: "FactoryBuilder.IFactory"):
            instance.config_table[self.attr_name] = self.value()

        def get_configurable_target(self) -> typing.Any:
            return self.configure

        def configure(self):
            raise NotImplementedError()

    class AnnotationFactoryConfigurator(IFactoryConfigurator):
        def __init__(self, config_name: str):
            super().__init__(config_name)
            self.pool = []

        def __call__(self, target: typing.Callable):
            self.pool.append(target)
            return target

        def get_configurable_target(self) -> typing.Any:
            return self.configure

        def configure(self, *args, **kwargs):
            if len(self.pool) > 0:
                for function in self.pool:
                    function(*args, *kwargs)
                return args[0]
            else:
                return self.pool[0](*args, **kwargs)

    class SetterFactoryConfigurator(IFactoryConfigurator):
        def __init__(
            self, func_name: str, attr_name: str, assert_type=object, default_value=None
        ):
            super().__init__(func_name)
            self.attr_name = attr_name
            self.assert_type = assert_type
            self.default_value = default_value

        def get_configurable_target(self) -> typing.Any:
            return self.configure

        def configure(self, instance, *args):
            if len(args) == 0:
                value = self.default_value
            else:
                (value,) = args
            assert isinstance(
                value, self.assert_type
            ), "type must be valid ({}, exptected {})".format(
                type(value), self.assert_type
            )
            instance.config_table[self.attr_name] = value
            return instance

    class FunctionAnnotator(IFactoryConfigurator):
        def __init__(self, config_name: str, attr_name: str):
            super().__init__(config_name)
            self.attr_name = attr_name

        def get_configurable_target(self) -> typing.Any:
            return self.configure

        def configure(self, instance, value=None):
            if value is None:
                return lambda function: self.configure(instance, function)
            instance.config_table[self.attr_name] = value
            return instance

    class FunctionStackedAnnotator(IFactoryConfigurator):
        def __init__(self, config_name: str, attr_name: str):
            super().__init__(config_name)
            self.attr_name = attr_name

        def prepare(self, instance: "FactoryBuilder.IFactory"):
            instance.config_table[self.attr_name] = []

        def get_configurable_target(self) -> typing.Any:
            return self.configure

        def configure(self, instance, value=None):
            if value is None:
                return lambda function: self.configure(instance, function)
            instance.config_table[self.attr_name].append(value)
            return instance

    class IFactoryClassBuilder(ABC):
        def prepare(self, instance: "FactoryBuilder.IFactory"):
            pass

        def apply(
            self,
            cls: typing.Type["FactoryBuilder.IFactory.IBuildFactoryContent"],
            instance: "FactoryBuilder.IFactory",
        ) -> typing.Type["FactoryBuilder.IFactory.IBuildFactoryContent"]:
            raise NotImplementedError()

    class AnnotationFactoryClassBuilder(IFactoryClassBuilder):
        def __init__(self):
            self.pool = []

        def __call__(self, function):
            self.pool.append(function)
            return function

        def apply(
            self,
            cls: typing.Type["FactoryBuilder.IFactory.IBuildFactoryContent"],
            instance: "FactoryBuilder.IFactory",
        ) -> typing.Type["FactoryBuilder.IFactory.IBuildFactoryContent"]:
            for function in self.pool:
                cls = function(cls, instance)
            return cls

    class IFactoryCopyOperation(ABC):
        def operate(
            self, old: "FactoryBuilder.IFactory", new: "FactoryBuilder.IFactory"
        ):
            raise NotImplementedError()

    class DefaultFactoryCopyOperation(IFactoryCopyOperation):
        def __init__(self, key: str, operation=lambda e: copy.deepcopy(e)):
            self.key = key
            self.operation = operation

        def operate(
            self, old: "FactoryBuilder.IFactory", new: "FactoryBuilder.IFactory"
        ):
            if self.key in old.config_table:
                new.config_table[self.key] = self.operation(old.config_table[self.key])

    class IFactory(ABC):
        """
        This is the core class for the system
        It manages all the cool stuff during factoring your class instance
        """

        class IBuildFactoryContent(ABC):
            pass

        def __init__(self, master: "FactoryBuilder", *args, **kwargs):
            if len(args) or len(kwargs):
                import traceback

                print(master, args, kwargs)
                traceback.print_stack()
            self.__dict__.update(
                {
                    "master": master,
                    "creation_arguments": (args, kwargs),
                    "template": [],
                    "base_classes": master.base_classes.copy(),
                    "config_table": {},
                }
            )

            for configurator in master.configurators:
                configurator.prepare(self)

        def __getattr__(self, item):
            if (
                "master" in self.__dict__
                and item in self.__dict__["master"].config_access_table
            ):
                return lambda *args, **kwargs: self.__dict__[
                    "master"
                ].config_access_table[item](self, *args, **kwargs)

            if item in self.__dict__:
                return self.__dict__[item]

            raise AttributeError("{} has no attribute '{}'".format(self, item))

        def __setattr__(self, key, value):
            if (
                "master" in self.__dict__
                and key in self.__dict__["master"].config_access_table
            ):
                self.__dict__["master"].config_access_table[key](self, value)
            else:
                super().__setattr__(key, value)

        def set_template(self):
            self.template.append(self.copy())
            return self

        def reset_template(self, all_templates=False):
            if all_templates:
                self.template.clear()
            else:
                assert len(self.template) > 0, "there must be a template to delete!"
                self.template.pop(-1)
            return self

        def set_to_template(self, pop=False):
            assert len(self.template) > 0, "there must be a template to reset to!"
            self.copy_from(self.template.pop(-1) if pop else self.template[-1])
            return self

        def copy(self) -> "FactoryBuilder.IFactory":
            new = self.master()
            try:
                new.creation_arguments = copy.deepcopy(self.creation_arguments)
                new.template = self.template.copy()
                new.base_classes = self.base_classes.copy()

                for operation in self.master.copy_operation_handlers:
                    operation.operate(self, new)
            except:
                logger.print_exception(
                    "during copying {} from {}".format(
                        self.config_table.setdefault("name", self), self.master.name
                    )
                )

            return new

        def add_base_class(self, cls):
            if cls not in self.base_classes:
                self.base_classes.append(cls)

        def __copy__(self):
            return self.copy()

        def copy_from(self, other: "FactoryBuilder.IFactory"):
            assert self.master == other.master, "cannot copy from an invalid source!"

            for operation in self.master.copy_operation_handlers:
                operation.operate(other, self)

            return self

        def finish(self):
            if len(self.template) > 0:
                build = self.copy().reset_template(True).finish()
                self.set_to_template(False)
                return build

            for builder in self.master.class_builders:
                builder.prepare(self)

            class BuildTarget(FactoryBuilder.IFactory.IBuildFactoryContent):
                pass

            for base in self.base_classes:

                class BuildTarget(BuildTarget, base):
                    pass

            for builder in self.master.class_builders:
                BuildTarget = builder.apply(BuildTarget, self)

            self.master.do_with_results(BuildTarget)

            return BuildTarget

    def __init__(
        self,
        name: str,
        base_class: typing.Type[mcpython.common.event.Registry.IRegistryContent],
        do_with_results=shared.registry.__call__,
    ):
        self.name = name
        self.base_classes = [base_class]
        self.do_with_results = do_with_results
        self.factory_class: typing.Optional[FactoryBuilder.IFactory] = None

        self.factory_class_modifiers: typing.List[
            typing.Type[FactoryBuilder.IFactoryClassModifier]
        ] = []
        self.configurators: typing.List[FactoryBuilder.IFactoryConfigurator] = []
        self.class_builders: typing.List[FactoryBuilder.IFactoryClassBuilder] = []
        self.copy_operation_handlers: typing.List[
            FactoryBuilder.IFactoryCopyOperation
        ] = []

        self.config_access_table: typing.Dict[str, typing.Callable] = {}

        self.dirty = True

    def register_modifier(self, modifier: typing.Type[IFactoryClassModifier]):
        self.dirty = True
        self.factory_class_modifiers.append(modifier)
        return modifier

    def register_configurator(self, configurator: IFactoryConfigurator):
        self.configurators.append(configurator)
        self.dirty = True
        return configurator

    def register_class_builder(self, builder: IFactoryClassBuilder):
        self.class_builders.append(builder)
        self.dirty = True
        return builder

    def register_copy_operation_handler(self, handler: IFactoryCopyOperation):
        self.copy_operation_handlers.append(handler)
        self.dirty = True
        return handler

    def __call__(self, *args, **kwargs) -> IFactory:
        if self.dirty:
            self.factory_class = self.create_class()
            self.dirty = False

        return self.factory_class(*args, **kwargs)

    def create_class(self) -> typing.Type[IFactory]:
        self.build_configuration_table()

        class Factory(FactoryBuilder.IFactory):
            def __init__(s, *args, **kwargs):
                super().__init__(self, *args, **kwargs)

        for modifier in self.factory_class_modifiers:
            Factory = modifier(self, Factory)

        return Factory

    def build_configuration_table(self):
        self.config_access_table.clear()

        for configurator in self.configurators:
            self.config_access_table[
                configurator.config_name
            ] = configurator.get_configurable_target()

    def register_direct_copy_attributes(self, *attributes, operation=copy.deepcopy):
        for attribute in attributes:
            if type(attribute) == tuple:
                attribute, *default = attribute
                self.register_configurator(
                    FactoryBuilder.InnerDefaultAttributeHelper(
                        attribute, attribute, lambda: operation(default[0])
                    )
                )
            self.register_copy_operation_handler(
                FactoryBuilder.DefaultFactoryCopyOperation(
                    attribute, operation=operation
                )
            )
