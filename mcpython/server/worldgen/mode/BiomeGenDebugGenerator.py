"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import math

import mcpython.common.mod.ModMcpython
import mcpython.server.worldgen.mode.DefaultOverWorldGenerator
import mcpython.server.worldgen.mode.IWorldGenConfig
import mcpython.server.worldgen.WorldGenerationTaskArrays
from mcpython import shared


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
        biome_map = chunk.get_map("minecraft:biome_map")
        height_map = chunk.get_map("minecraft:height_map")

        for dx in range(16):
            for dz in range(16):
                x, z = cx * 16 + dx, cz * 16 + dz
                biome = biome_map.get_at_xz(x, z)
                block = cls.BIOME_TO_BLOCK[biome]
                chunk.add_block(
                    (x, 0, z), block, block_update=False, block_update_self=False
                )

                height_map.set_at_xz(x, z, [(0, 5)])

        if shared.world.get_active_player().gamemode != 3:
            shared.world.get_active_player().set_gamemode(3)
        shared.world.get_active_player().flying = True


shared.world_generation_handler.register_world_gen_config(DebugBiomeWorldGenerator)

mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:post",
    DebugBiomeWorldGenerator.generate_table,
    info="constructing debug world info",
)
