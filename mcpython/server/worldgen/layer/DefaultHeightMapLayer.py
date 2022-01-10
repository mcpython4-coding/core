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

    base_noise = (
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME,
            scale=10 ** 2 * 0.5,
            dimensions=2,
            octaves=3,
            merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
        )
    )
    base_noise.merger_config = [3, 2, 1]

    inter_noise_1 = (
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_inter_1",
            scale=10,
            dimensions=2,
            octaves=4,
            merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
        )
    )
    inter_noise_2 = (
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_inter_2",
            scale=10,
            dimensions=2,
            octaves=4,
            merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
        )
    )

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
        base_noise_map = cls.base_noise.calculate_area((x, z), (x + 16, z + 16))
        inter_noise_map_1 = cls.inter_noise_1.calculate_area((x, z), (x + 16, z + 16))
        inter_noise_map_2 = cls.inter_noise_1.calculate_area((x, z), (x + 16, z + 16))

        await asyncio.gather(
            *(
                cls.get_height_at(height_map, config, chunk, x, z, v1, v2, v3)
                for ((x, z), v1), (_, v2), (_, v3) in zip(
                    base_noise_map, inter_noise_map_1, inter_noise_map_2
                )
            )
        )

    @classmethod
    async def get_height_at(cls, height_map, config, chunk, x, z, height, v2, v3):
        # todo: make configurable by world generator, decide biome based on height
        start, end = 20, 40
        end *= config.max_height_factor
        height *= end - start
        height += start
        height = round(height)

        # todo: do some more special stuff here!
        if v2 > 0.9:
            total_height = height + round(20 * v3)

            if v2 > 0.98:
                info = [(1, total_height)]
            else:
                inter = round((total_height - height) * (v2 - 0.9) * 10)
                info = [(1, height), (height + inter, total_height)]

        else:
            info = [(1, height)]

        height_map.set_at_xz(x, z, info)
