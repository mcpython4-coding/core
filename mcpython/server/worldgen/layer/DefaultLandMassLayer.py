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
class DefaultLandMassLayer(ILayer):
    NAME = "minecraft:landmass_default"

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME + "_3",
        scale=10**2,
        octaves=3,
        dimensions=2,
        merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
    )

    @staticmethod
    def normalize_config(config: LayerConfig):
        if config.masses is None:
            config.masses = config.world_generator_config.LANDMASSES

    @classmethod
    async def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        land_map = chunk.get_map("minecraft:landmass_map")

        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))

        for (x, z), v in noise_map:
            v *= len(config.masses)
            v = round(v)
            if v == len(config.masses):
                v = 0
            land_map.set_at_xz(x, z, config.masses[v])
