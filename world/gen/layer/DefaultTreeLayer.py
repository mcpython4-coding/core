"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

from world.gen.layer.Layer import Layer, LayerConfig
import globals as G
import random
import world.Chunk


@G.worldgenerationhandler
class DefaultTreeLayer(Layer):
    @staticmethod
    def get_name() -> str:
        return "tree_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        cx, cz = chunk.position
        cx *= 16
        cz *= 16
        for x in range(16):
            for z in range(16):
                chunk.chunkgenerationtasks.append([DefaultTreeLayer.generate_position, [cx+x, cz+z, chunk, config], {}])

    @staticmethod
    def generate_position(x, z, chunk, config):
        treemap = chunk.get_value("treeblocked")
        if (x, z) in treemap: return  # is an tree nearby?
        biome = G.biomehandler.biomes[chunk.get_value("biomemap")[(x, z)]]
        height = chunk.get_value("heightmap")[(x, z)][0][1]
        trees = biome.get_trees()
        for IFeature, chance in trees:
            if random.randint(1, chance) == 1:
                IFeature.place(chunk.dimension, x, height+1, z)
                for dx in range(-2, 3):
                    for dz in range(-2, 3):
                        treemap.append((x+dx, z+dz))
                return


authcode = world.Chunk.Chunk.add_default_attribute("treeblocked", DefaultTreeLayer, [])

