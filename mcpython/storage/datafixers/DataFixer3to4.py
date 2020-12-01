"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
import mcpython.storage.datafixers.IDataFixer
import mcpython.storage.serializer.Chunk
import os


@G.registry
class DataFixer3to4(mcpython.storage.datafixers.IDataFixer.IStorageVersionFixer):
    NAME = "minecraft:storage_fixer_3_4"

    FIXES_FROM = 3
    FIXES_TO = 4

    @classmethod
    def apply(cls, savefile):
        savefile.apply_part_fixer("minecraft:chunk_data_fixer_storage_3_4")


@G.registry
class ChunkDataFixer3to4(mcpython.storage.serializer.Chunk.ChunkDataFixer):
    NAME = "minecraft:chunk_data_fixer_storage_3_4"

    @classmethod
    def fix(cls, savefile, dimension, region, chunk, cdata):
        blocks = cdata["blocks"]
        cdata["blocks"] = {}
        for position in blocks:
            cdata["blocks"][(position[0] - chunk[0] * 16, position[1],
                             position[2] - chunk[2] * 16)] = blocks[position]
        return cdata
