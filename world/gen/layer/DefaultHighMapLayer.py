"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

from world.gen.layer.Layer import Layer, LayerConfig
import globals as G
import random
import opensimplex
import world.Chunk


@G.worldgenerationhandler
class DefaultHighMapLayer(Layer):
    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 2

    @staticmethod
    def get_name() -> str:
        return "highmap_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultHighMapLayer.generate_highmap, [chunk, config], {}])

    @classmethod
    def generate_highmap(cls, chunk, config):
        highmap = chunk.get_value("highmap")
        cx, cz = chunk.position
        factor = 10**config.size
        for x in range(cx*16, cx*16+16):
            for z in range(cz*16, cz*16+16):
                highmap[(x, z)] = cls.get_high_at(chunk, x, z, factor)
                # chunk.add_add_block_gen_task((x, highmap[(x, z)][0][1], z), "minecraft:stone")

    @classmethod
    def get_high_at(cls, chunk, x, z, factor) -> list:
        v = DefaultHighMapLayer.noise.noise2d(x / factor, z / factor) * 0.5 + 0.5
        biomemap = chunk.get_value("biomemap")
        biome = G.biomehandler.biomes[biomemap[(x, z)]]
        r = biome.get_high_range()
        v *= r[1] - r[0]
        v += r[0]
        info = [(1, round(v))]
        return info


authcode = world.Chunk.Chunk.add_default_attribute("highmap", DefaultHighMapLayer, {})

