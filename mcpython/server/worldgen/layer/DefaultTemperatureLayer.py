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
class DefaultTemperatureLayer(Layer):
    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @classmethod
    def update_seed(cls):
        seed = G.world.config["seed"]
        cls.noise = opensimplex.OpenSimplex(seed=seed * 100 + 5)

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "min"):
            config.min = -0.5
        if not hasattr(config, "max"):
            config.max = 2.0
        if not hasattr(config, "size"):
            config.size = 2

    NAME = "minecraft:temperature_map"

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        temperature_map = chunk.get_value("minecraft:temperature_map")
        factor = 10 ** config.size
        r = [config.min, config.max]
        for x in range(cx * 16, cx * 16 + 16):
            for z in range(cz * 16, cz * 16 + 16):
                v = DefaultTemperatureLayer.noise.noise2d(x / factor, z / factor)
                v = v / 2.0 + 0.5
                v *= abs(r[0] - r[1])
                v += r[0]
                temperature_map[(x, z)] = v


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "minecraft:temperature_map", DefaultTemperatureLayer, {}
)

mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "seed:set", DefaultTemperatureLayer.update_seed
)
