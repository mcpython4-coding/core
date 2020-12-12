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
import mcpython.server.worldgen.biome.BiomeHandler
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig
import mcpython.common.world.Chunk
import mcpython.common.world.AbstractInterface


@G.world_generation_handler
class DefaultBiomeMapILayer(ILayer):
    DEPENDS_ON = ["minecraft:landmass_default"]

    noise: opensimplex.OpenSimplex = None

    @classmethod
    def update_seed(cls):
        seed = G.world.config["seed"]
        cls.noise = opensimplex.OpenSimplex(seed=seed * 100)

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 1.5

    NAME = "minecraft:biome_map_default"

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        biomemap = chunk.get_value("biome_map")
        landmap = chunk.get_value("landmass_map")
        temperaturemap = chunk.get_value("minecraft:temperature_map")
        factor = 10 ** config.size
        for x in range(cx * 16, cx * 16 + 16):
            for z in range(cz * 16, cz * 16 + 16):
                landmass = landmap[(x, z)]
                v = (
                    DefaultBiomeMapILayer.noise.noise3d(
                        x / factor, z / factor, x * z / factor ** 2
                    )
                    * 0.5
                    + 0.5
                )
                biomemap[(x, z)] = G.biome_handler.get_biome_at(
                    landmass, config.dimension, v, temperaturemap[(x, z)]
                )
        chunk.set_value("biome_map", biomemap)


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "biome_map", DefaultBiomeMapILayer, {}
)

mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "seed:set", DefaultBiomeMapILayer.update_seed
)
