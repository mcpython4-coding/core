"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import math

from mcpython import shared
import mcpython.server.worldgen.mode.IWorldGenConfig
import mcpython.server.worldgen.mode.DefaultOverWorldGenerator
import mcpython.common.mod.ModMcpython


class DebugBiomeWorldGenerator(
    mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig
):
    NAME = "minecraft:debug_biome_world_generator"
    DISPLAY_NAME = "BIOME DEBUG GENERATOR"
    DIMENSION = "minecraft:overworld"

    LAYERS = [
        "minecraft:landmass_default",
        "minecraft:temperature_map",
        "minecraft:biome_map_default",
    ]

    BIOME_SOURCE = mcpython.server.worldgen.mode.IWorldGenConfig.DefaultBiomeSource
    BIOMES = (
        mcpython.server.worldgen.mode.DefaultOverWorldGenerator.DefaultOverworldGenerator.BIOMES
    )
    LANDMASSES = (
        mcpython.server.worldgen.mode.DefaultOverWorldGenerator.DefaultOverworldGenerator.LANDMASSES
    )

    BIOME_TO_BLOCK = {}

    @classmethod
    def generate_table(cls):
        blocks = list(shared.registry.get_by_name("minecraft:block").entries.keys())
        blocks.sort()
        i = 0
        for a in cls.BIOMES.values():
            for biome_array in a.values():
                for biome in biome_array:
                    cls.BIOME_TO_BLOCK[biome] = blocks[i]
                    i += 1

    @classmethod
    def on_chunk_generation_finished(
        cls,
        chunk,
    ):
        cx, cz = chunk.position
        biome_map = chunk.get_value("minecraft:biome_map")
        for dx in range(16):
            for dz in range(16):
                x, z = cx * 16 + dx, cz * 16 + dz
                biome = biome_map[(x, z)]
                block = cls.BIOME_TO_BLOCK[biome]
                chunk.add_block((x, 0, z), block)


shared.world_generation_handler.register_world_gen_config(DebugBiomeWorldGenerator)

mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:post",
    DebugBiomeWorldGenerator.generate_table,
    info="constructing debug world info",
)
