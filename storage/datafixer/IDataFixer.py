"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import event.Registry
import mod.ModMcpython


class DataFixerException(Exception): pass


class IDataFixer(event.Registry.IRegistryContent):
    TYPE = "minecraft:datafixer"
    # NAME should be: "<version from>-<version to>:<part>"

    TRANSFORMS = (None, None)  # from, to
    PART = None  # which part it fixes, only one per part is executed

    DEPENDS = []  # an list of fixer parts which should be executed first

    @classmethod
    def fix(cls, savefile):
        raise NotImplementedError()


class IGeneralDataFixer(event.Registry.IRegistryContent):
    """
    Every version supported by datafixer need this.
    It provides information what to fix on load and what can wait
    """

    TYPE = "minecraft:general_datafixer"
    # NAME should be the version this data fixer group is assigned to

    LOAD_FIXES = []  # an list of parts to fix an or (partname, kwargs)

    UPGRADES_TO = None  # which version this datafixer upgrades to


datafixerregistry = event.Registry.Registry("datafixers", ["minecraft:datafixer"])
generaldatafixerregistry = event.Registry.Registry("generaldatafixers", ["minecraft:general_datafixer"])


def load_general_fixer():
    from storage.datafixer import (DataFixer1to2, DataFixer2to3)


def load_fixer():
    pass


mod.ModMcpython.mcpython.eventbus.subscribe("stage:datafixer:general", load_general_fixer)
mod.ModMcpython.mcpython.eventbus.subscribe("stage:datafixer:parts", load_fixer)

