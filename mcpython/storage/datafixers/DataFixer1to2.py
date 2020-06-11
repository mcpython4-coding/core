"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.storage.datafixers.IDataFixer
import mcpython.storage.serializer.Chunk
import os


@G.registry
class DataFixer1to2(mcpython.storage.datafixers.IDataFixer.IStorageVersionFixer):
    NAME = "minecraft:storage_fixer_1_2"

    FIXES_FROM = 1
    FIXES_TO = 2

    @classmethod
    def apply(cls, savefile):
        savefile.apply_part_fixer("minecraft:chunk_data_fixer_storage_1_2")


@G.registry
class ChunkDataFixer1to2(mcpython.storage.serializer.Chunk.ChunkDataFixer):
    NAME = "minecraft:chunk_data_fixer_storage_1_2"

    FIXES_FROM = 1
    FIXES_TO = 2

    @classmethod
    def fix(cls, savefile, dimension, region, chunk, cdata):
        if "temperature" in cdata:
            del cdata["temperature"]
        if "landmass" in cdata["maps"]:
            landmass_map = cdata["maps"]["landmass"]
            del cdata["maps"]["landmass"]
            cdata["maps"]["landmass_map"] = []
            cdata["maps"]["landmass_palette"] = []
            for i in range(len(landmass_map)):
                mass = landmass_map[i]
                if mass not in cdata["maps"]["landmass_palette"]:
                    index = len(cdata["maps"]["landmass_palette"])
                    cdata["maps"]["landmass_palette"].append(mass)
                else:
                    index = cdata["maps"]["landmass_palette"].index(mass)
                cdata["maps"]["landmass_map"].append(index)
        return cdata

