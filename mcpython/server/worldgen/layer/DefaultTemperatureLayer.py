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
class DefaultTemperatureLayer(ILayer):
    NAME = "minecraft:temperature_map"

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME,
        scale=10**2,
        dimensions=2,
        octaves=3,
        merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
    )

    @staticmethod
    def normalize_config(config: LayerConfig):
        if config.temperature_min is None:
            config.temperature_min = -0.5
        if config.temperature_max is None:
            config.temperature_max = 2.0

    @classmethod
    async def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        x, z = chunk.position[0] * 16, chunk.position[1] * 16

        temperature_map = chunk.get_map("minecraft:temperature_map")
        r = [config.temperature_min, config.temperature_max]

        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))

        for (x, z), v in noise_map:
            v *= abs(r[0] - r[1])
            v += r[0]
            temperature_map.set_at_xz(x, z, v)
