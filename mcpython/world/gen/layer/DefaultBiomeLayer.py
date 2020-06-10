"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import random

import opensimplex

import globals as G
import mcpython.event.EventHandler
import mcpython.world.Chunk
import mcpython.world.gen.biome.BiomeHandler
from mcpython.world.gen.layer.Layer import Layer, LayerConfig


@G.worldgenerationhandler
class DefaultBiomeMapLayer(Layer):
    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @classmethod
    def update_seed(cls):
        seed = G.world.config["seed"]
        cls.noise = opensimplex.OpenSimplex(seed=seed * 100)

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 1.5

    NAME = "biomemap_default"

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        biomemap = chunk.get_value("biomemap")
        landmap = chunk.get_value("landmassmap")
        temperaturemap = chunk.get_value("temperaturemap")
        factor = 10**config.size
        for x in range(cx*16, cx*16+16):
            for z in range(cz*16, cz*16+16):
                landmass = landmap[(x, z)]
                v = DefaultBiomeMapLayer.noise.noise3d(x/factor, z/factor, x*z/factor**2) * 0.5 + 0.5
                biomemap[(x, z)] = G.biomehandler.get_biome_at(landmass, config.dimension, v, temperaturemap[(x, z)])
        chunk.set_value("biomemap", biomemap)


authcode = mcpython.world.Chunk.Chunk.add_default_attribute("biomemap", DefaultBiomeMapLayer, {})

mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("seed:set", DefaultBiomeMapLayer.update_seed)
