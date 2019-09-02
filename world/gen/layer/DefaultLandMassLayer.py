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
class DefaultLandMassLayer(Layer):
    noise1 = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))
    noise2 = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))
    noise3 = opensimplex.OpenSimplex(seed=random.randint(-10000, 10000))

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "masses"):
            config.masses = ["land"]
            # todo: add underwaterbiomes
        if not hasattr(config, "size"):
            config.size = 1

    @staticmethod
    def get_name() -> str:
        return "landmass_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultLandMassLayer.generate_landmass, [chunk, config], {}])

    @staticmethod
    def generate_landmass(chunk, config):
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
                """
                if v < 0:
                    chunk.add_add_block_gen_task((x, 5, z), "minecraft:stone")
                else:
                    chunk.add_add_block_gen_task((x, 5, z), "minecraft:dirt")
                """


authcode = world.Chunk.Chunk.add_default_attribute("landmassmap", DefaultLandMassLayer, {})

