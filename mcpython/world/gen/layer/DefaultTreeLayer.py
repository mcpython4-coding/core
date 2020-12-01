"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""

import random

from mcpython import globals as G
import mcpython.world.Chunk
from mcpython.world.gen.layer.Layer import Layer, LayerConfig


@G.worldgenerationhandler
class DefaultTreeLayer(Layer):
    NAME = "tree_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        cx *= 16
        cz *= 16
        for x in range(16):
            for z in range(16):
                reference.schedule_invoke(DefaultTreeLayer.generate_position, cx+x, cz+z, reference, config)

    @staticmethod
    def generate_position(x, z, reference, config):
        chunk = reference.chunk
        treemap = chunk.get_value("treeblocked")
        if (x, z) in treemap: return  # is an tree nearby?
        biome = G.biomehandler.biomes[chunk.get_value("biomemap")[(x, z)]]
        height = chunk.get_value("heightmap")[(x, z)][0][1]
        trees = biome.get_trees()
        # todo: make noise-based
        for IFeature, chance in trees:
            if random.randint(1, chance) == 1:
                IFeature.place(chunk.dimension, x, height+1, z)
                for dx in range(-2, 3):
                    for dz in range(-2, 3):
                        treemap.append((x+dx, z+dz))
                return


authcode = mcpython.world.Chunk.Chunk.add_default_attribute("treeblocked", DefaultTreeLayer, [])
