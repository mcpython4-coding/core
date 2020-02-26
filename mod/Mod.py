"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.EventBus
import event.EventHandler
import traceback


class ModDependency:
    def __init__(self, name: str, versions=None):
        """
        creates an new mod dependency instance. need to be assigned with another mod
        :param name: the name of the mod
        :param versions: None if all, version if only one, list of versions if only a group,
                         list of False and than versions for not (excluding)

        """
        self.name = name
        self.versions = versions

    def arrival(self) -> bool:
        if self.name not in G.modloader.mods: return False
        if self.versions is None: return True
        real_mod = G.modloader.mods[self.name]
        if self.versions == real_mod.version: return True
        if type(self.versions) == list:
            if real_mod.version in self.versions: return True
        return False

    def get_version(self):
        return G.modloader.mods[self.name].version

    def get_loading_stage(self):
        pass

    def __str__(self):
        if not self.versions:
            return self.name
        elif type(self.versions) == str:
            if self.versions[0]:
                return "{} in any of the following versions: ".format(self.name) + (", ".join(self.versions) if type(
                    self.versions) != str else self.versions)
            else:
                return "{} in none any of the following versions: ".format(self.name) + ", ".join(self.versions[1:])
        else:
            return "{} in version {}".format(self.name, self.versions)


class Mod:
    """
    class for mods. for creating an new mod, create an instance of this
    """

    def __init__(self, name: str, version):
        """
        creates an new mod
        :param name: the name of the mod
        """
        self.name = name
        self.eventbus: event.EventBus.EventBus = event.EventHandler.LOADING_EVENT_BUS.create_sub_bus(
            crash_on_error=False)
        self.dependinfo = [[] for _ in range(5)]  # need, possible, not possible, before, after
        self.path = None
        self.version = version
        self.package = None
        G.modloader.add_to_add(self)

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

