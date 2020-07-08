"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import mcpython.storage.datafixers.IDataFixer
import mcpython.storage.serializer.Chunk
import os


@G.registry
class DataFixer2to3(mcpython.storage.datafixers.IDataFixer.IStorageVersionFixer):
    NAME = "minecraft:storage_fixer_2_3"

    FIXES_FROM = 2
    FIXES_TO = 3

    @classmethod
    def apply(cls, savefile):
        savefile.apply_part_fixer("minecraft:block_fixer_chest_storage_2_3")


@G.registry
class ChunkFixer2to3(mcpython.storage.serializer.Chunk.BlockPartFixer):
    NAME = "minecraft:block_fixer_chest_storage_2_3"

    TARGET_BLOCK_NAME = "minecraft:chest"

    @classmethod
    def fix(cls, savefile, dimension, region, chunk, palette):
        palette["custom"] = {"model": palette["custom"], "loot_table": None}
        return palette

