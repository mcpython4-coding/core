"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython
import deprecation


@deprecation.deprecated("dev3-1", "a1.3.0")
class DataFixerException(Exception): pass


@deprecation.deprecated("dev3-1", "a1.3.0")
class IDataFixer(mcpython.common.event.Registry.IRegistryContent):
    TYPE = "minecraft:datafixer"
    TRANSFORMS = (None, None)
    PART = None
    DEPENDS = []

    @classmethod
    @deprecation.deprecated("dev3-1", "a1.3.0")
    def fix(cls, savefile):
        pass


@deprecation.deprecated("dev3-1", "a1.3.0")
class IGeneralDataFixer(mcpython.common.event.Registry.IRegistryContent):
    TYPE = "minecraft:general_datafixer"
    LOAD_FIXES = []
    UPGRADES_TO = None


datafixerregistry = None  # mcpython.event.Registry.Registry("datafixers", ["minecraft:datafixer"])
generaldatafixerregistry = None  # mcpython.event.Registry.Registry("generaldatafixers", ["minecraft:general_datafixer"])


@deprecation.deprecated("dev3-1", "a1.3.0")
def load_general_fixer():
    from mcpython.server.storage.datafixer import DataFixer3to4, DataFixer1to2, DataFixer2to3, DataFixer4to5


@deprecation.deprecated("dev3-1", "a1.3.0")
def load_fixer():
    pass
