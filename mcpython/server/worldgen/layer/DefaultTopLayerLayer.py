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
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig
import mcpython.server.worldgen.noise.INoiseImplementation


@shared.world_generation_handler
class DefaultTopLayerLayer(ILayer):
    NAME = "minecraft:top_layer_default"
    DEPENDS_ON = ["minecraft:heightmap_default", "minecraft:biome_map_default"]

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME,
        dimensions=2,
        scale=10 ** 3,
        octaves=5,
        merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
    )

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))
        for (x, z), v in noise_map:
            reference.schedule_invoke(cls.generate_xz, reference, x, z, config, v)

    @staticmethod
    def generate_xz(reference, x, z, config, noise_value):
        chunk = reference.chunk
        heightmap = chunk.get_value("heightmap")
        mheight = heightmap[(x, z)][0][1]
        biome = shared.biome_handler.biomes[
            chunk.get_value("minecraft:biome_map")[(x, z)]
        ]
        r = biome.get_top_layer_height_range((x, z), chunk.get_dimension())
        noise_value *= r[1] - r[0]
        noise_value += r[0]
        height = round(noise_value)
        decorators = biome.get_top_layer_configuration(
            height, (x, z), chunk.get_dimension()
        )
        for i in range(height):
            y = mheight - (height - i - 1)
            block = reference.get_block((x, y, z), chunk)
            if block and (block if type(block) == str else block.NAME) in [
                "minecraft:stone"
            ]:
                try:
                    if i == height - 1:
                        reference.schedule_block_add((x, y, z), decorators[i])
                    else:
                        reference.schedule_block_add(
                            (x, y, z), decorators[i], immediate=i >= height - 1
                        )
                except IndexError:
                    pass
