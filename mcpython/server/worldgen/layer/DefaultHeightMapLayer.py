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
import asyncio
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
    DEPENDS_ON = []

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

        # todo: can we optimize this preparation by sending prepared noise values directly to the async part
        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))
        await asyncio.gather(
            *(
                cls.get_height_at(height_map, config, chunk, x, z, v)
                for (x, z), v in noise_map
            )
        )

    @classmethod
    async def get_height_at(cls, height_map, config, chunk, x, z, v):
        # todo: make configurable by world generator, decide biome based on height
        start, end = 20, 40
        end *= config.max_height_factor
        v *= end - start
        v += start
        info = [(1, round(v))]  # todo: do some more special stuff here!
        height_map.set_at_xz(x, z, info)
