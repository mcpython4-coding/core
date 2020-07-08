"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""

import random

import opensimplex

import globals as G
import mcpython.event.EventHandler
import mcpython.world.Chunk
from mcpython.world.gen.layer.Layer import Layer, LayerConfig


@G.worldgenerationhandler
class DefaultLandMassLayer(Layer):
    noise1 = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))
    noise2 = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))
    noise3 = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @classmethod
    def update_seed(cls):
        seed = G.world.config["seed"]
        cls.noise1 = opensimplex.OpenSimplex(seed=seed * 100 + 2)
        cls.noise2 = opensimplex.OpenSimplex(seed=seed * 100 + 3)
        cls.noise3 = opensimplex.OpenSimplex(seed=seed * 100 + 4)

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "masses"):
            config.masses = ["land"]
            # todo: add underwaterbiomes
        if not hasattr(config, "size"):
            config.size = 1

    NAME = "landmass_default"

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        landmap = chunk.get_value("landmassmap")
        factor = 10**config.size
        for x in range(cx*16, cx*16+16):
            for z in range(cz*16, cz*16+16):
                v = sum([DefaultLandMassLayer.noise1.noise2d(x/factor, z/factor) * 0.5 + 0.5,
                         DefaultLandMassLayer.noise2.noise2d(x/factor, z/factor) * 0.5 + 0.5,
                         DefaultLandMassLayer.noise3.noise2d(x/factor, z/factor) * 0.5 + 0.5]) / 3
                v *= len(config.masses)
                v = round(v)
                if v == len(config.masses):
                    v = 0
                landmap[(x, z)] = config.masses[v]


authcode = mcpython.world.Chunk.Chunk.add_default_attribute("landmassmap", DefaultLandMassLayer, {})

mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("seed:set", DefaultLandMassLayer.update_seed)
