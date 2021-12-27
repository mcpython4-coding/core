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

import mcpython.engine.event.SingleInvokeAsyncEventBus
import mcpython.engine.event.EventBus
import mcpython.engine.event.EventHandler
from mcpython import shared


class ModDependency:
    """
    Class for a dependency-like reference to a mod
    """

    def __init__(self, name: str, version_min=None, version_max=None, versions=None):
        """
        Creates a new mod dependency instance. Needs to be assigned to another mod. If no version is specified,
        all versions match this dependency.
        :param name: the name of the mod to depend on
        :param version_min: the minimum version to use, including
        :param version_max: the maximum version to use, including
        :param versions: set when an list of possible versions should be used. Can contain min-value and
            tuples of (min, max) [a whole range]

        """
        self.name = name
        self.version_range = (
            self.convert_any_to_version_tuple(version_min),
            self.convert_any_to_version_tuple(version_max),
        )
        self.versions = (
            None
            if versions is None
            else [self.convert_any_to_version_tuple(e) for e in versions]
        )

    @classmethod
    def convert_any_to_version_tuple(cls, a):
        if a is None:
            return None
        if type(a) == tuple:
            return a
        if type(a) == str:
            return tuple([int(e) for e in a.split(".")])
        raise ValueError("invalid version entry '{}' of type '{}'".format(a, type(a)))

    def arrival(self) -> bool:
        if self.name not in shared.mod_loader.mods:
            return False
        mod = shared.mod_loader.mods[self.name]
        if self.version_range[0] is not None:
            if self.version_range[1] is not None:
                return self.test_match(mod.version, self.version_range)
            return self.test_match(mod.version, self.version_range[0])
        if self.versions is None:
            return True
        if type(self.versions) == list:
            return any([self.test_match(mod.version, e) for e in self.versions])
        return False

    @classmethod
    def test_match(cls, version, args: tuple) -> bool:
        """
        Will test if the dependency is matching
        :param version: the version found
        :param args: optional args found
        """
        if type(version) == str:
            version = version.split(".")
        if type(args[0]) == int:
            return version >= args
        if len(args) == 1:
            return version >= args[0]
        if len(args) == 2:
            return args[1] >= version >= args[0]

        raise RuntimeError(version, args)

    def get_version(self):
        """
        Getter for the real version of the mod specified by this
        """
        return shared.mod_loader.mods[self.name].version

    def __str__(self):
        """
        Returns a string representing this class
        """
        if self.version_range[0] is not None:
            if self.version_range[1] is not None:
                return "'{}' in version from version {} to {}".format(
                    self.name,
                    ".".join([str(e) for e in self.version_range[0]]),
                    ".".join([str(e) for e in self.version_range[1]]),
                )

            return "'{}' in version starting from version {}".format(
                self.name, ".".join([str(e) for e in self.version_range[0]])
            )

        if self.versions is None or len(self.versions) == 0:
            return "'{}' in any version".format(self.name)

        cond = []
        for entry in self.versions:
            if type(entry[0]) == int:
                cond.append(".".join([str(e) for e in entry]))
            elif len(entry) == 1:
                cond.append(".".join([str(e) for e in entry[0]]))
            elif len(entry) == 2:
                cond.append(
                    "{} to {}".format(
                        ".".join([str(e) for e in entry[0]]),
                        ".".join([str(e) for e in entry[1]]),
                    )
                )
            else:
                raise ValueError(
                    "can't cast entry '{}' to valid version identifier".format(entry)
                )

        return "'{}' in version(s) {}".format(self.name, " or ".join(cond))


class Mod:
    """
    Class for mods. For creating a new mod, create an instance of this or define an entry in the latest version in your
    mod.json file. Can be subclassed for custom mod specs
    """

    def __init__(
        self,
        name: str,
        version: typing.Union[tuple, str, set, list],
        version_name: str = None,
        add_to_mod_loader=True,
    ):
        """
        Creates a new mod
        :param name: the name of the mod
        :param version: a tuple of CONSTANT length across ALL versions representing the version of the mod
        :param add_to_mod_loader: if to register to the mod loader
        """
        # Parse the version information
        if type(version) != tuple:
            if type(version) == str:
                version = (
                    tuple([int(e) for e in version.split(".")])
                    if version.isdigit()
                    else (0, 1, 0)
                )
            elif type(version) in (set, list):
                version = tuple(version)
            else:
                raise ValueError(
                    "can't use mod named '{}' as it provides an not-valid version '{}'".format(
                        name, version
                    )
                )

        self.name = name

        # The mod event bus
        self.eventbus: mcpython.engine.event.SingleInvokeAsyncEventBus.SingleInvokeAsyncEventBus = (
            mcpython.engine.event.SingleInvokeAsyncEventBus.SingleInvokeAsyncEventBus()
        )

        # need, possible, not possible, before, after, only with, only without
        self.depend_info = [[] for _ in range(7)]

        self.path = None  # the path this mod is loaded from
        self.container = None  # the mod loader container this is in
        self.version = version  # the version of the mod, as an tuple
        self.version_name = version_name
        self.package = None  # the package where the mod-file was found
        self.resource_access = None  # where to load resources from

        self.server_only = False

        if add_to_mod_loader and shared.mod_loader:
            shared.mod_loader.add_to_add(self)

    def mod_string(self) -> str:
        """
        Will transform the mod into a string for display purposes
        """
        return "{} ({})".format(self.name, ".".join([str(e) for e in self.version])) + (
            "" if self.version_name is None else " as " + self.version_name
        )

    def __repr__(self):
        return "Mod@{}({},{})".format(hex(id(self))[2:], self.name, self.version)

    def add_load_default_resources(self, path_name=None):
        """
        Adds the default resource locations for loading into the system
        :param path_name: optional: the namespace to load
        """
        if path_name is None:
            path_name = self.name

        import mcpython.common.data.ResourcePipe

        self.eventbus.subscribe(
            "stage:mod:init",
            mcpython.common.data.ResourcePipe.handler.register_for_mod(
                self.name, path_name
            ),
            info="adding resource load subscriptions",
        )

    def add_dependency(self, depend: typing.Union[str, ModDependency]):
        """
        Will add a dependency into the system; The selected mod will be loaded before this one
        :param depend: the mod to depend on
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))

        self.depend_info[0].append(depend)
        self.depend_info[4].append(depend)
        return self

    def add_not_load_dependency(self, depend: typing.Union[str, ModDependency]):
        """
        Will add a dependency without setting load_after for this mod
        :param depend: the mod to depend on
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[0].append(depend)
        return self

    def add_not_compatible(self, depend: typing.Union[str, ModDependency]):
        """
        Sets a mod for not loadable together with another one, meaning incompatibility, for example
        :param depend: the mod to not load with
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[2].append(depend)
        return self

    def add_load_before_if_arrival(self, depend: typing.Union[str, ModDependency]):
        """
        Will load these mod before the selected, but will not set the dependency
        :param depend: the mod to load before
        :return:
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[1].append(depend)
        self.depend_info[3].append(depend)
        return self

    def add_load_after_if_arrival(self, depend: typing.Union[str, ModDependency]):
        """
        Will load these mod after the selected, but will not set the dependency
        :param depend: the mod to load after
        :return:
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[1].append(depend)
        self.depend_info[4].append(depend)
        return self

    def add_load_only_when_arrival(self, depend: typing.Union[str, ModDependency]):
        """
        Will only load the mod if another one is arrival, but will not cause an dependency error when not arrival
        :param depend: the mod to check for
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[5].append(depend)
        return self

    def add_load_only_when_not_arrival(self, depend: typing.Union[str, ModDependency]):
        """
        Will only load the mod if another one is not arrival, but will not cause an dependency error when arrival,
        :param depend: the mod to check for
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[6].append(depend)
        return self

    def check_dependencies(self, mod_loader, mod_info) -> bool:
        for depend in self.depend_info[0]:
            if not depend.arrival():
                if shared.event_handler.call_cancelable(
                    "minecraft:modloader:missing_dependency", mod_loader, self, depend
                ):
                    mod_loader.error_builder.println(
                        "- Mod '{}' needs mod {} which is not provided".format(
                            self.name, depend
                        )
                    )
                    return False

        for depend in self.depend_info[2]:
            if depend.arrival():
                if shared.event_handler.call_cancelable(
                    "minecraft:modloader:incompatible_mod", mod_loader, self, depend
                ):
                    mod_loader.error_builder.println(
                        "- Mod '{}' is incompatible with {} which is provided".format(
                            self.name, depend
                        )
                    )
                    return False

        # todo: do we want two more events here?
        for depend in self.depend_info[5]:
            if not depend.arrival():
                del mod_info[self.name]
                del mod_loader.mods[self.name]

        for depend in self.depend_info[6]:
            if depend.arrival():
                del mod_info[self.name]
                del mod_loader.mods[self.name]

        return True
