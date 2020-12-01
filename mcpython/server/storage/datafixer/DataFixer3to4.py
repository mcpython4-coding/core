"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals as G
import mcpython.storage.datafixer.IDataFixer
import deprecation


@deprecation.deprecated("dev3-1", "a1.3.0")
class GeneralFix(mcpython.storage.datafixer.IDataFixer.IGeneralDataFixer):
    NAME = 3
    LOAD_FIXES = []
    UPGRADES_TO = 4


@deprecation.deprecated("dev3-1", "a1.3.0")
class ChunkFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    NAME = "3-4:minecraft:chunk"
    TRANSFORMS = (3, 4)
    PART = "minecraft:chunk"

    @classmethod
    @deprecation.deprecated("dev3-1", "a1.3.0")
    def fix(cls, savefile, dimension, region):
        data = savefile.access_file_pickle(
            "dim/{}/{}_{}.region".format(dimension, *region)
        )
        if data is None:
            return
        if data["version"] != 3:
            return
        data["version"] = 4
        for chunk in data.keys():
            if chunk == "version":
                continue
            cdata = data[chunk]
            blocks = cdata["blocks"]
            cdata["blocks"] = {}
            for position in blocks:
                cdata["blocks"][
                    (
                        position[0] - chunk[0] * 16,
                        position[1],
                        position[2] - chunk[2] * 16,
                    )
                ] = blocks[position]
        savefile.dump_file_pickle(
            "dim/{}/{}_{}.region".format(dimension, *region), data
        )


@G.registry
@deprecation.deprecated("dev3-1", "a1.3.0")
class InventoryFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    NAME = "3-4:minecraft:inventory_file"
    TRANSFORMS = (3, 4)
    PART = "minecraft:inventory_file"

    @classmethod
    @deprecation.deprecated("dev3-1", "a1.3.0")
    def fix(cls, savefile, path, file=None):
        data = savefile.access_file_pickle(file)
        data["version"] = 4
        savefile.dump_file_pickle(file, data)
