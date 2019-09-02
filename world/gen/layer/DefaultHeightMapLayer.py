"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

from world.gen.layer.Layer import Layer, LayerConfig
import globals as G
import random
import opensimplex
import world.Chunk


@G.worldgenerationhandler
class DefaultHeightMapLayer(Layer):
    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 2

    @staticmethod
    def get_name() -> str:
        return "heightmap_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultHeightMapLayer.generate_heightmap, [chunk, config], {}])

    @classmethod
    def generate_heightmap(cls, chunk, config):
        heightmap = chunk.get_value("heightmap")
        cx, cz = chunk.position
        factor = 10**config.size
        for x in range(cx*16, cx*16+16):
            for z in range(cz*16, cz*16+16):
                heightmap[(x, z)] = cls.get_height_at(chunk, x, z, factor)
                # chunk.add_add_block_gen_task((x, heightmap[(x, z)][0][1], z), "minecraft:stone")

    @classmethod
    def get_height_at(cls, chunk, x, z, factor) -> list:
        v = DefaultHeightMapLayer.noise.noise2d(x / factor, z / factor) * 0.5 + 0.5
        biomemap = chunk.get_value("biomemap")
        biome = G.biomehandler.biomes[biomemap[(x, z)]]
        r = biome.get_height_range()
        v *= r[1] - r[0]
        v += r[0]
        info = [(1, round(v))]
        return info


authcode = world.Chunk.Chunk.add_default_attribute("heightmap", DefaultHeightMapLayer, {})

