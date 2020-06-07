"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.storage.datafixer.IDataFixer


@G.registry
class GeneralFix(mcpython.storage.datafixer.IDataFixer.IGeneralDataFixer):
    NAME = 2

    LOAD_FIXES = []

    UPGRADES_TO = 3


@G.registry
class ChunkFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    # NAME should be: "<version from>-<version to>:<part>"
    NAME = "2-3:minecraft:chunk"

    TRANSFORMS = (2, 3)  # from, to
    PART = "minecraft:chunk"  # which part it fixes, only one per part is executed

    @classmethod
    def fix(cls, savefile, dimension, region):
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: return
        if data["version"] != 2: return
        data["version"] = 3
        for chunk in data:
            if chunk != "version":
                chunk_data = data[chunk]
                for palette in chunk_data["block_palette"]:
                    if palette["name"] == "minecraft:chest":
                        palette["custom"] = {"model": palette["custom"], "loot_table": None}
        savefile.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)


@G.registry
class InventoryFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    NAME = "2-3:minecraft:inventory_file"
    TRANSFORMS = (2, 3)  # from, to
    PART = "minecraft:inventory_file"  # which part it fixes, only one per part is executed

    @classmethod
    def fix(cls, savefile, path, file=None):
        data = savefile.access_file_pickle(file)
        data["version"] = 3
        savefile.dump_file_pickle(file, data)
