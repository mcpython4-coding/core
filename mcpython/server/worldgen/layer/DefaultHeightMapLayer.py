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
import mcpython.common.event.EventHandler
import mcpython.common.world.Chunk
from mcpython.server.worldgen.layer.Layer import Layer, LayerConfig


@G.worldgenerationhandler
class DefaultHeightMapLayer(Layer):
    DEPENDS_ON = ["minecraft:biome_map_default"]

    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @classmethod
    def update_seed(cls):
        seed = G.world.config["seed"]
        cls.noise = opensimplex.OpenSimplex(seed=seed * 100 + 1)

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 2

    NAME = "minecraft:heightmap_default"

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        heightmap = chunk.get_value("heightmap")
        cx, cz = chunk.position
        factor = 10 ** config.size
        for x in range(cx * 16, cx * 16 + 16):
            for z in range(cz * 16, cz * 16 + 16):
                heightmap[(x, z)] = cls.get_height_at(chunk, x, z, factor)

    @classmethod
    def get_height_at(cls, chunk, x, z, factor) -> list:
        v = DefaultHeightMapLayer.noise.noise2d(x / factor, z / factor) * 0.5 + 0.5
        biome_map = chunk.get_value("biome_map")
        biome = G.biomehandler.biomes[biome_map[(x, z)]]
        r = biome.get_height_range()
        v *= r[1] - r[0]
        v += r[0]
        info = [(1, round(v))]
        return info


authcode = mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "heightmap", DefaultHeightMapLayer, {}
)

mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "seed:set", DefaultHeightMapLayer.update_seed
)
