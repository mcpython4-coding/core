"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""

import random

import mcpython.server.worldgen.noise.NoiseManager

from mcpython import shared
import mcpython.common.event.EventHandler
import mcpython.common.world.Chunk
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@shared.world_generation_handler
class DefaultLandMassLayer(ILayer):
    NAME = "minecraft:landmass_default"

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME + "_3",
        scale=10 ** 2,
        octaves=3,
        dimensions=2,
        merger=mcpython.server.worldgen.noise.NoiseManager.INNER_MERGE,
    )

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "masses"):
            config.masses = config.world_generator_config.LANDMASSES

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        land_map = chunk.get_value("minecraft:landmass_map")
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))
        for (x, z), v in noise_map:
            v *= len(config.masses)
            v = round(v)
            if v == len(config.masses):
                v = 0
            land_map[(x, z)] = config.masses[v]


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "minecraft:landmass_map", DefaultLandMassLayer, {}
)
