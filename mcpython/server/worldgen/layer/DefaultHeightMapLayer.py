"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""

import random

import mcpython.server.worldgen.noise.NoiseManager
import mcpython.server.worldgen.noise.INoiseImplementation

from mcpython import shared
import mcpython.common.event.EventHandler
import mcpython.common.world.Chunk
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
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        heightmap = chunk.get_value("heightmap")

        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))

        for (x, z), v in noise_map:
            heightmap[(x, z)] = cls.get_height_at(config, chunk, x, z, v)

    @classmethod
    def get_height_at(cls, config, chunk, x, z, v) -> list:
        biome_map = chunk.get_value("minecraft:biome_map")
        biome = shared.biome_handler.biomes[biome_map[(x, z)]]
        start, end = biome.get_height_range()
        end *= config.max_height_factor
        v *= end - start
        v += start
        info = [(1, round(v))]  # todo: do some more special stuff here!
        return info


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "heightmap", DefaultHeightMapLayer, {}
)
