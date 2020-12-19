"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.common.event.EventBus
import mcpython.common.event.EventHandler
import typing


class ModDependency:
    """
    class for an dependency-like reference to an mod
    """

    def __init__(self, name: str, version_min=None, version_max=None, versions=None):
        """
        creates an new mod dependency instance. need to be assigned with another mod. if no version(s) is/are specified,
        all are allowed
        :param name: the name of the mod
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
        if self.name not in G.mod_loader.mods:
            return False
        mod = G.mod_loader.mods[self.name]
        if self.version_range[0] is not None:
            if self.version_range[1] is not None:
                return self.__test_for(mod.version, self.version_range)
            return self.__test_for(mod.version, self.version_range[0])
        if self.versions is None:
            return True
        if type(self.versions) == list:
            return any([self.__test_for(mod.version, e) for e in self.versions])
        return False

    @classmethod
    def __test_for(cls, version, args: tuple) -> bool:
        """
        will test for the arrival of the dependency
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

    def get_version(self):
        """
        gets the real version of the mod specified by this
        """
        return G.mod_loader.mods[self.name].version

    def __str__(self):
        """
        returns an stringifies version dependency
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
    class for mods. For creating an new mod, create an instance of this or define an entry in the latest version in your
    mod.json file.
    """

    def __init__(
        self,
        name: str,
        version: typing.Union[tuple, str, set, list],
        version_name: str = None,
    ):
        """
        creates an new mod
        :param name: the name of the mod
        :param version: an tuple of CONSTANT length across ALL versions representing the version of the mod
        """
        if type(version) != tuple:
            if type(version) == str:
                version = tuple([int(e) for e in version.split(".")])
            elif type(version) in (set, list):
                version = tuple(version)
            else:
                raise ValueError(
                    "can't use mod named '{}' as it provides an not-valid version '{}'".format(
                        name, version
                    )
                )
        self.name = name
        self.eventbus: mcpython.common.event.EventBus.EventBus = (
            mcpython.common.event.EventHandler.LOADING_EVENT_BUS.create_sub_bus(
                crash_on_error=False
            )
        )
        self.depend_info = [
            [] for _ in range(7)
        ]  # need, possible, not possible, before, after, only with, only without
        self.path = None
        self.version = version  # the version of the mod, as an tuple
        self.version_name = version_name
        self.package = None  # the package where the mod-file was found
        G.mod_loader.add_to_add(self)

    def mod_string(self):
        """
        will transform the mod into an string
        """
        return "{} ({})".format(self.name, ".".join([str(e) for e in self.version])) + (
            "" if self.version_name is None else " as " + self.version_name
        )

    def __repr__(self):
        return "Mod({},{})".format(self.name, self.version)

    def add_load_default_resources(self, path_name=None):
        """
        adds the default resource locations for loading into the system
        :param path_name: optional: the namespace to load
        """
        if path_name is None:
            path_name = self.name
        import mcpython.common.mod.ResourcePipe

        self.eventbus.subscribe(
            "stage:mod:init",
            lambda: mcpython.common.mod.ResourcePipe.handler.register_for_mod(
                self.name, path_name
            ),
            info="adding resources",
        )

    def add_dependency(self, depend: typing.Union[str, ModDependency]):
        """
        will add an dependency into the system; The selected mod will be loaded before this one
        :param depend: the mod to depend on
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[0].append(depend)
        self.depend_info[4].append(depend)
        return self

    def add_not_load_dependency(self, depend: typing.Union[str, ModDependency]):
        """
        will add an dependency without setting load_after for this mod
        :param depend: the mod to depend on
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[0].append(depend)
        return self

    def add_not_compatible(self, depend: typing.Union[str, ModDependency]):
        """
        sets an mod for not loadable together with another one (e.g. useful on mod rename)
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
        Will only load the mod if another one is arrival, but will not cause an dependency error in case of not arrival
        :param depend: the mod to check for
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[5].append(depend)
        return self

    def add_load_only_when_not_arrival(self, depend: typing.Union[str, ModDependency]):
        """
        Will only load the mod if another one is not arrival, but will not cause an dependency error in case of arrival,
        Useful for e.g. API's
        :param depend: the mod to check for
        """
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.depend_info[6].append(depend)
        return self
