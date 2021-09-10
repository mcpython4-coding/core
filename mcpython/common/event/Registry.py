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
import typing

import mcpython.common.data.serializer.tags.ITagTarget
import mcpython.engine.event.EventHandler
from mcpython import shared
from mcpython.common.event.api import AbstractRegistry, IRegistryContent
from mcpython.common.event.DeferredRegistryHelper import DeferredRegistry
from mcpython.engine import logger


class Registry(AbstractRegistry):
    """
    One registry for one object-type

    Holds information about it and does some magic to handle it

    Supports "XY" in registry and registry["XY"], but no write this way
    """

    def __init__(
        self,
        name: str,
        registry_type_names: list,
        phase: typing.Optional[str] = None,
        injection_function=None,
        allow_argument_injection=False,
        class_based=True,
        dump_content_in_saves=True,
        register_to_shared_registry=True,
        sync_via_network=True,
        registry_sync_package_class=None,
    ):
        super().__init__()

        self.name = name
        self.phase = phase
        self.registry_type_names = registry_type_names
        self.injection_function = injection_function
        self.allow_argument_injection = allow_argument_injection

        self.entries = {}
        self.full_entries = {}

        self.class_based = class_based
        self.dump_content_in_saves = dump_content_in_saves

        self.sync_via_network = sync_via_network
        self.registry_sync_package_class = registry_sync_package_class

        if register_to_shared_registry:
            shared.registry.registries[name] = self

        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
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
        overwrite_existing=True,
    ):
        """
        Registers an obj to this registry

        When locked, a RuntimeError is raised
        When an object with the name exists, and overwrite_existing is False, a RuntimeError is raised
        When the object does not extend IRegistryContent, a ValueError is raised
        When the object NAME-attribute is not set, a ValueError is raised
        """

        if self.locked:
            raise RuntimeError(f"registry {self.name} is locked!")

        if not (
            isinstance(obj, IRegistryContent)
            if not self.class_based
            else issubclass(obj, IRegistryContent)
        ):
            raise ValueError(
                f"can only register stuff created from IRegistryContent, not {obj}"
            )

        if obj.NAME == "minecraft:unknown_registry_content":
            raise ValueError(
                f"object {obj} has no name set, and as such cannot be registered!"
            )

        if obj.NAME in self.entries and not overwrite_existing:
            raise RuntimeError(
                f"could not register object {obj.NAME} ({obj}) into registry {self.name} as an object with this name exists"
            )

        self.entries[obj.NAME] = obj
        self.full_entries[obj.NAME] = obj

        # todo: what to do if an object exists HERE?
        if isinstance(obj.NAME, str):
            self.full_entries[obj.NAME.split(":")[-1]] = obj

        if self.injection_function:
            self.injection_function(self, obj)

        # Call the event function on the object
        obj.on_register(self)

        return obj

    def entries_iterator(self) -> typing.Iterable[IRegistryContent]:
        if self.locked:
            return self.entries.keys()
        return self.entries.copy().keys()

    def elements_iterator(self) -> typing.Iterable[IRegistryContent]:
        if self.locked:
            return self.entries.values()
        return self.entries.copy().values()

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def is_valid_key(self, key: str):
        return key in self.full_entries

    def get(self, key: str, default=False):
        if default is not False and key not in self.full_entries:
            return default
        return self.full_entries[key]

    def create_deferred(self, mod_name: str, *args, **kwargs):
        return DeferredRegistry(self, mod_name, *args, **kwargs)


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

    def __call__(self, obj):
        if not issubclass(obj, IRegistryContent):
            raise ValueError(
                "can't register. Object {} is NO sub-class of IRegistryContent".format(
                    obj
                )
            )

        for registry in self.registries.values():
            if registry.is_valid(obj):
                registry.register(obj)
                return obj

        raise ValueError(
            "could not register entry {} as no registry for type '{}' was found".format(
                obj, obj.TYPE
            )
        )

    def get_by_name(self, name: str) -> typing.Optional[Registry]:
        return None if name not in self.registries else self.registries[name]

    def register(self, *args, **kwargs):
        return self(*args, **kwargs)

    def delayed_register(self, mod: str, phase: str):
        return lambda obj: shared.mod_loader(mod, phase)(lambda: self.register(obj))

    def create_deferred(self, registry: str, mod_name: str):
        return DeferredRegistry(self.get_by_name(registry), mod_name)

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
