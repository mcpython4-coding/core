"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

from world.gen.layer.Layer import Layer, LayerConfig
import globals as G
import random
import opensimplex


@G.worldgenerationhandler
class DefaultTopLayerLayer(Layer):
    noise = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "size"):
            config.size = 3

    @staticmethod
    def get_name() -> str:
        return "toplayer_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultTopLayerLayer.generate_chunk, [chunk, config], {}])

    @staticmethod
    def generate_chunk(chunk, config):
        factor = 10 ** config.size
        for x in range(chunk.position[0]*16, chunk.position[0]*16+16):
            for z in range(chunk.position[1]*16, chunk.position[1]*16+16):
                chunk.chunkgenerationtasks.append([DefaultTopLayerLayer.generate_xz, [chunk, x, z, config, factor], {}])

    @staticmethod
    def generate_xz(chunk, x, z, config, factor):
        heightmap = chunk.get_value("heightmap")
        mheight = heightmap[(x, z)][0][1]
        biome = G.biomehandler.biomes[chunk.get_value("biomemap")[(x, z)]]
        noisevalue = DefaultTopLayerLayer.noise.noise2d(x/factor, z/factor) * 0.5 + 0.5
        r = biome.get_top_layer_height_range()
        noisevalue *= r[1] - r[0]
        noisevalue += r[0]
        height = round(noisevalue)
        decorators = biome.get_top_layer_configuration(height)
        for i in range(height):
            y = mheight - (height-i-1)
            block = chunk.get_block((x, y, z)) if chunk.is_position_blocked((x, y, z)) else None
            if block and (block if type(block) == str else block.get_name()) in ["minecraft:stone"]:
                chunk.add_add_block_gen_task((x, y, z), decorators[i], immediate=i == height - 1)



