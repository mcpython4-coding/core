"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.storage.datafixers.IDataFixer
import mcpython.storage.serializer.Chunk


@G.registry
class DataFixer4to5(mcpython.storage.datafixers.IDataFixer.IStorageVersionFixer):
    NAME = "minecraft:storage_fixer_4_5"

    FIXES_FROM = 4
    FIXES_TO = 5

    @classmethod
    def apply(cls, savefile):
        savefile.apply_part_fixer("minecraft:chunk_data_fixer_storage_4_5")


@G.registry
class ChunkDataFixer4to5(mcpython.storage.serializer.Chunk.ChunkDataFixer):
    NAME = "minecraft:chunk_data_fixer_storage_4_5"

    @classmethod
    def fix(cls, savefile, dimension, region, chunk, cdata):
        if "entities" not in cdata:
            cdata["entities"] = []
        return cdata
