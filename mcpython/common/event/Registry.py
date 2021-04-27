"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from abc import ABC

from mcpython import shared, logger
import mcpython.logger
import mcpython.common.event.EventHandler
import typing
import mcpython.common.data.tags.ITagTarget


class IRegistryContent(mcpython.common.data.tags.ITagTarget.ITagTarget):
    NAME = "minecraft:unknown_registry_content"
    TYPE = "minecraft:unknown_registry_content_type"

    @classmethod
    def on_register(cls, registry):
        pass

    INFO = None  # can be used to display any special info in e.g. /registryinfo-command

    # returns some information about the class stored in registry. used in saves to determine if registry was changed,
    # so could also include an version. Must be pickle-able
    @classmethod
    def compressed_info(cls):
        return cls.NAME


class Registry:
    def __init__(
        self,
        name: str,
        registry_type_names: list,
        phase: str,
        injection_function=None,
        allow_argument_injection=False,
        class_based=True,
        dump_content_in_saves=True,
    ):
        assert ":" in name, "name must be name-spaced"
        self.name = name
        self.phase = phase
        self.registry_type_names = registry_type_names
        self.injection_function = injection_function
        self.allow_argument_injection = allow_argument_injection
        self.entries = {}
        self.full_entries = {}
        self.locked = False
        self.class_based = class_based
        shared.registry.registries[name] = self
        self.dump_content_in_saves = dump_content_in_saves

        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "mod_loader:load_finished", self.lock
        )

    def __contains__(self, item):
        return item in self.full_entries

    def __getitem__(self, item):
        return self.full_entries[item]

    def is_valid(self, obj: IRegistryContent):
        return not self.locked and obj.TYPE in self.registry_type_names

    def register(
        self,
        obj: typing.Union[IRegistryContent, typing.Type[IRegistryContent]],
        override_existing=True,
    ):
        """
        Registers an obj to this registry
        """
        if self.locked:
            logger.print_stack(
                "[WARN] can't register object '{}' to locked registry '{}'. Skipping registering...".format(
                    obj, self.name
                )
            )
            return
        if obj.NAME == "minecraft:unknown_registry_content":
            logger.print_stack(
                "can't register unnamed object '{}'".format(obj),
                "every registry object MUST have an unique name",
            )
            return
        if obj.NAME in self.entries and override_existing:
            logger.println(
                "[INFO] skipping register of {} named '{}' into registry '{}' as currently arrival".format(
                    obj, obj.NAME, self.name
                )
            )
            return

        self.entries[obj.NAME] = obj
        self.full_entries[obj.NAME] = obj
        if hasattr(obj.NAME, "split"):
            self.full_entries[obj.NAME.split(":")[-1]] = obj
        if self.injection_function:
            self.injection_function(self, obj)
        obj.on_register(self)

    def entries_iterator(self) -> typing.Iterable[IRegistryContent]:
        if self.locked:
            return self.entries.keys()
        return self.entries.copy().keys()

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def is_valid_key(self, key: str):
        return key in self.full_entries

    def get(self, key: str):
        return self.full_entries[key]


class RegistryInjectionHolder:
    def __init__(self, *args, **kwargs):  # todo: do something with the args and kwargs!
        self.args = args
        self.kwargs = kwargs
        self.injectable = None

    def __call__(self, obj):
        self.injectable = obj
        shared.registry(self)


class RegistryHandler:
    def __init__(self):
        self.registries = {}

    def __call__(self, *args, **kwargs):
        if len(args) == len(kwargs) == 0:
            raise ValueError("can't register. no object provided")

        elif len(args) > 1 or len(kwargs) > 0:  # create an injectable object instance
            return RegistryInjectionHolder(*args, **kwargs)

        elif type(args[0]) == RegistryInjectionHolder:
            if not issubclass(args[0].inhectable, IRegistryContent):
                raise ValueError(
                    "can't register. Object {} is NO sub-class of IRegistryContent".format(
                        args[0].injectable
                    )
                )
            for registry in self.registries.values():
                if registry.allow_argument_injection and registry.is_valid(
                    args[0].injectable
                ):
                    registry.register(args[0])
                return args[0].injectable
            raise ValueError(
                "could not register entry {} as no registry was found".format(args[0])
            )

        else:
            if not issubclass(args[0], IRegistryContent):
                raise ValueError(
                    "can't register. Object {} is NO sub-class of IRegistryContent".format(
                        args[0]
                    )
                )
            for registry in self.registries.values():
                if registry.is_valid(args[0]):
                    registry.register(args[0])
                    return args[0]
            raise ValueError(
                "could not register entry {} as no registry for type '{}' was found".format(
                    args[0], args[0].TYPE
                )
            )

    def get_by_name(self, name: str) -> typing.Optional[Registry]:
        return None if name not in self.registries else self.registries[name]

    def register(self, *args, **kwargs):
        return self(*args, **kwargs)

    def async_register(self, mod: str, phase: str):
        return lambda obj: shared.mod_loader(mod, phase)(lambda: self.register(obj))

    def create_deferred(self, registry: str, mod_name: str):
        return DeferredRegistryPipe(self.get_by_name(registry), mod_name)

    def print_content(self, registry: str, namespace=None):
        namespace = "" if namespace is None else namespace + ":"

        r = self.get_by_name(registry)
        if r is None:
            logger.println(f"registry {registry} not found!")
            return

        logger.println(f"values in registry '{registry}'")
        for key in r.entries.keys():
            if not isinstance(key, str) or key.startswith(namespace):
                element = r.entries[key]
                logger.println(
                    " -",
                    key,
                    element,
                    element.INFO if element.INFO is not None else "",
                    sep=" ",
                )


shared.registry = RegistryHandler()


class DeferredRegistryPipe:
    """
    Base class for deferred registries
    """

    def __init__(self, registry: Registry, modname: str):
        self.registry = registry
        self.modname = modname

    def run_later(self, lazy: typing.Callable[[], IRegistryContent]):
        shared.mod_loader(self.modname, self.registry.phase)(lazy)
