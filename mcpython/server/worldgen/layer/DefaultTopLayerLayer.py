"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""

import random

import opensimplex

from mcpython import shared as G
from mcpython.server.worldgen.layer.Layer import Layer, LayerConfig


@G.worldgenerationhandler
class DefaultTopLayerLayer(Layer):
    DEPENDS_ON = ["minecraft:heightmap_default", "minecraft:biome_map_default"]

    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 3

    NAME = "minecraft:top_layer_default"

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        factor = 10 ** config.size
        for x in range(chunk.position[0] * 16, chunk.position[0] * 16 + 16):
            for z in range(chunk.position[1] * 16, chunk.position[1] * 16 + 16):
                reference.schedule_invoke(
                    cls.generate_xz, reference, x, z, config, factor
                )

    @staticmethod
    def generate_xz(reference, x, z, config, factor):
        chunk = reference.chunk
        heightmap = chunk.get_value("heightmap")
        mheight = heightmap[(x, z)][0][1]
        biome = G.biomehandler.biomes[chunk.get_value("biome_map")[(x, z)]]
        noise_value = (
            DefaultTopLayerLayer.noise.noise2d(x / factor, z / factor) * 0.5 + 0.5
        )
        r = biome.get_top_layer_height_range()
        noise_value *= r[1] - r[0]
        noise_value += r[0]
        height = round(noise_value)
        decorators = biome.get_top_layer_configuration(height)
        for i in range(height):
            y = mheight - (height - i - 1)
            block = reference.get_block((x, y, z), chunk)
            if block and (block if type(block) == str else block.NAME) in [
                "minecraft:stone"
            ]:
                if i == height - 1:
                    reference.schedule_block_add((x, y, z), decorators[i])
                else:
                    reference.schedule_block_add(
                        (x, y, z), decorators[i], immediate=i >= height - 1
                    )
