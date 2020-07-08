"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import mcpython.storage.datafixer.IDataFixer
import deprecation


@deprecation.deprecated("dev3-1", "a1.3.0")
class GeneralFix(mcpython.storage.datafixer.IDataFixer.IGeneralDataFixer):
    NAME = 4
    LOAD_FIXES = []
    UPGRADES_TO = 5


@deprecation.deprecated("dev3-1", "a1.3.0")
class ChunkFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    NAME = "4-5:minecraft:chunk"
    TRANSFORMS = (4, 5)
    PART = "minecraft:chunk"

    @classmethod
    @deprecation.deprecated("dev3-1", "a1.3.0")
    def fix(cls, savefile, dimension, region):
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: return
        if data["version"] != 4: return
        data["version"] = 5
        for chunk in data.keys():
            if chunk == "version": continue
            cdata = data[chunk]
            if "entities" not in cdata:
                cdata["entities"] = []
        savefile.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)


@deprecation.deprecated("dev3-1", "a1.3.0")
class InventoryFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    NAME = "4-5:minecraft:inventory_file"
    TRANSFORMS = (4, 5)
    PART = "minecraft:inventory_file"

    @classmethod
    def fix(cls, savefile, path, file=None):
        data = savefile.access_file_pickle(file)
        data["version"] = 5
        savefile.dump_file_pickle(file, data)

