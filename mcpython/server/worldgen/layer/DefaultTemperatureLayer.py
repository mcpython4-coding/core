"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""

import random

import mcpython.server.worldgen.noise.NoiseManager

from mcpython import shared
import mcpython.common.event.EventHandler
import mcpython.common.world.Chunk
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig
import mcpython.server.worldgen.noise.INoiseImplementation


@shared.world_generation_handler
class DefaultTemperatureLayer(ILayer):
    NAME = "minecraft:temperature_map"

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME,
        scale=10 ** 2,
        dimensions=2,
        octaves=3,
        merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
    )

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "min"):
            config.min = -0.5
        if not hasattr(config, "max"):
            config.max = 2.0

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        temperature_map = chunk.get_value("minecraft:temperature_map")
        r = [config.min, config.max]
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))
        for (x, z), v in noise_map:
            v *= abs(r[0] - r[1])
            v += r[0]
            temperature_map[(x, z)] = v


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "minecraft:temperature_map", DefaultTemperatureLayer, {}
)
