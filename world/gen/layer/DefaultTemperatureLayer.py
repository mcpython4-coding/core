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
class DefaultTemperatureLayer(Layer):
    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "min"):
            config.min = -0.5
        if not hasattr(config, "max"):
            config.max = 2.
        if not hasattr(config, "size"):
            config.size = 2

    @staticmethod
    def get_name() -> str:
        return "temperaturemap"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultTemperatureLayer.generate_temperature, [chunk, config], {}])

    @staticmethod
    def generate_temperature(chunk, config):
        cx, cz = chunk.position
        temperaturemap = chunk.get_value("temperaturemap")
        factor = 10**config.size
        r = [config.min, config.max]
        for x in range(cx*16, cx*16+16):
            for z in range(cz*16, cz*16+16):
                v = DefaultTemperatureLayer.noise.noise2d(x/factor, z/factor)
                v = v / 2. + .5
                v *= abs(r[0] - r[1])
                v += r[0]
                temperaturemap[(x, z)] = v


authcode = world.Chunk.Chunk.add_default_attribute("temperaturemap", DefaultTemperatureLayer, {})

