"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.server.storage.datafixers.IDataFixer
import mcpython.server.storage.serializer.Chunk


@G.registry
class DataFixer5to6(mcpython.server.storage.datafixers.IDataFixer.IStorageVersionFixer):
    NAME = "minecraft:storage_fixer_5_6"

    FIXES_FROM = 5
    FIXES_TO = 6

    @classmethod
    def apply(cls, savefile):
        savefile.apply_part_fixer("minecraft:region_data_fixer_storage_5_6")


@G.registry
class RegionDataFixer5to6(mcpython.server.storage.serializer.Chunk.RegionDataFixer):
    NAME = "minecraft:region_data_fixer_storage_5_6"

    @classmethod
    def fix(cls, savefile, dimension, region, data):
        if "version" in data:
            del data["version"]
        return data
