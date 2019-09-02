"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import world.gen.biome.BiomeHandler
from world.gen.layer.Layer import Layer, LayerConfig
import globals as G
import random
import opensimplex
import world.Chunk


@G.worldgenerationhandler
class DefaultBiomeMapLayer(Layer):
    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 1.5

    @staticmethod
    def get_name() -> str:
        return "biomemap_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultBiomeMapLayer.generate_biomemap, [chunk, config], {}])

    @staticmethod
    def generate_biomemap(chunk, config):
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
        chunk.set_value("biomemap", biomemap, authcode)


authcode = world.Chunk.Chunk.add_default_attribute("biomemap", DefaultBiomeMapLayer, {})

