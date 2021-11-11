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

import random

import mcpython.common.world.Chunk
import mcpython.engine.event.EventHandler
import mcpython.server.worldgen.noise.INoiseImplementation
import mcpython.server.worldgen.noise.NoiseManager
from mcpython import shared
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@shared.world_generation_handler
class DefaultHeightMapLayer(ILayer):
    NAME = "minecraft:heightmap_default"
    DEPENDS_ON = ["minecraft:biome_map_default"]

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME,
        scale=10 ** 2,
        dimensions=2,
        octaves=5,
        merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
    )
    noise.merger_config = [3, 2, 1]

    @staticmethod
    def normalize_config(config: LayerConfig):
        if config.max_height_factor is None:
            config.max_height_factor = 1

    @classmethod
    async def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        height_map = chunk.get_map("minecraft:height_map")
        biome_map = chunk.get_map("minecraft:biome_map")

        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))

        for (x, z), v in noise_map:
            height_map.set_at_xz(
                x, z, cls.get_height_at(config, chunk, x, z, v, biome_map)
            )

    @classmethod
    def get_height_at(cls, config, chunk, x, z, v, biome_map) -> list:
        biome = shared.biome_handler.biomes[biome_map.get_at_xz(x, z)]
        start, end = biome.get_height_range()
        end *= config.max_height_factor
        v *= end - start
        v += start
        info = [(1, round(v))]  # todo: do some more special stuff here!
        return info
