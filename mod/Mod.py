"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.EventBus
import event.EventHandler


class ModDependency:
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
        self.version_range = (self.convert_any_to_version_tuple(version_min),
                              self.convert_any_to_version_tuple(version_max))
        self.versions = None if versions is None else [self.convert_any_to_version_tuple(e) for e in versions]

    @classmethod
    def convert_any_to_version_tuple(cls, a):
        if a is None: return None
        if type(a) == tuple: return a
        if type(a) == str: return tuple([int(e) for e in a.split(".")])
        raise ValueError("invalid version entry '{}' of type '{}'".format(a, type(a)))

    def arrival(self) -> bool:
        if self.name not in G.modloader.mods: return False
        mod = G.modloader.mods[self.name]
        if self.version_range[0] is not None:
            if self.version_range[1] is not None:
                return self.__testfor(mod.version, self.version_range)
            return self.__testfor(mod.version, self.version_range[0])
        if self.versions is None: return True
        if type(self.versions) == list:
            return any([self.__testfor(mod.version, e) for e in self.versions])
        return False

    def __testfor(self, version, args: tuple) -> bool:
        if type(args[0]) == int: return version >= args
        if len(args) == 1: return version >= args[0]
        if len(args) == 2: return args[1] >= version >= args[0]

    def get_version(self):
        return G.modloader.mods[self.name].version

    def __str__(self):
        if self.version_range[0] is not None:
            if self.version_range[1] is not None:
                return "'{}' in version from version {} to {}".format(self.name,
                                                                      ".".join([str(e) for e in self.version_range[0]]),
                                                                      ".".join([str(e) for e in self.version_range[1]]))
            return "'{}' in version starting from version {}".format(self.name, ".".join(
                [str(e) for e in self.version_range[0]]))
        if self.versions is None or len(self.versions) == 0: return "'{}' in any version".format(self.name)
        cond = []
        for entry in self.versions:
            if type(entry[0]) == int: cond.append(".".join([str(e) for e in entry]))
            elif len(entry) == 1: cond.append(".".join([str(e) for e in entry[0]]))
            elif len(entry) == 2: cond.append("{} to {}".format(".".join([str(e) for e in entry[0]]),
                                                                ".".join([str(e) for e in entry[1]])))
            else:
                raise ValueError("can't cast entry '{}' to valid version identifier".format(entry))
        return "'{}' in version(s) {}".format(self.name, " or ".join(cond))


class Mod:
    """
    class for mods. for creating an new mod, create an instance of this
    """

    def __init__(self, name: str, version: tuple):
        """
        creates an new mod
        :param name: the name of the mod
        :param version: an tuple of CONSTANT length across ALL versions representing the version of the mod
        """
        if type(version) != tuple:
            raise ValueError("can't use mod named '{}' as it provides an not-valid version '{}'".format(
                name, version))
        self.name = name
        self.eventbus: event.EventBus.EventBus = event.EventHandler.LOADING_EVENT_BUS.create_sub_bus(
            crash_on_error=False)
        self.dependinfo = [[] for _ in range(7)]  # need, possible, not possible, before, after, only with, only without
        self.path = None
        self.version = version
        self.package = None
        G.modloader.add_to_add(self)

    def mod_string(self):
        return "{} ({})".format(self.name, ".".join([str(e) for e in self.version]))

    def add_load_default_resources(self):
        import ResourceLocator
        self.eventbus.subscribe("stage:mod:init",
                                lambda: ResourceLocator.add_resources_by_modname(self.name, self.name),
                                info="adding resources")

    def add_dependency(self, depend):
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.dependinfo[0].append(depend)
        self.dependinfo[4].append(depend)

    def add_not_load_dependency(self, depend):
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.dependinfo[0].append(depend)

    def add_not_compatible(self, depend):
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.dependinfo[2].append(depend)

    def add_load_before_if_arrival(self, depend):
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.dependinfo[1].append(depend)
        self.dependinfo[3].append(depend)

    def add_load_after_if_arrival(self, depend):
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.dependinfo[1].append(depend)
        self.dependinfo[4].append(depend)

    def add_load_only_when_arrival(self, depend):
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.dependinfo[5].append(depend)

    def add_load_only_when_not_arrival(self, depend):
        if type(depend) == str:
            depend = ModDependency(*depend.split("|"))
        self.dependinfo[6].append(depend)

