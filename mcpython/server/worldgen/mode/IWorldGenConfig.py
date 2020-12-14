import typing
from mcpython import shared
import mcpython.server.worldgen.layer.DefaultBiomeLayer


class IBiomeSource:
    @classmethod
    def get_biome_at(cls, x, z, noises, landmass, config, temperature) -> str:
        raise NotImplementedError()


class SingleBiomeSource(IBiomeSource):
    def __init__(self, biome_name: str):
        self.biome_name = biome_name

    def get_biome_at(self, x, z, noises, landmass, config, temperature) -> str:
        return self.biome_name


class DefaultBiomeSource(IBiomeSource):
    @classmethod
    def get_biome_at(cls, x, z, noises, landmass, config, temperature) -> str:
        v = (
            mcpython.server.worldgen.layer.DefaultBiomeLayer.DefaultBiomeMapLayer.noise.noise3d(
                x / config.size, z / config.size, x * z / config.size ** 2
            )
            * 0.5
            + 0.5
        )
        return shared.biome_handler.get_biome_at(
            landmass, v, temperature, config.world_generator_config.BIOMES
        )


class IWorldGenConfig:
    NAME = None
    DISPLAY_NAME = None

    BIOMES = []
    BIOME_SOURCE: typing.Type[IBiomeSource] = SingleBiomeSource("minecraft:void")

    GENERATION_LAYERS = []

    LANDMASSES = []
    LAYERS = []

    @classmethod
    def on_chunk_generation_finished(cls, chunk):
        pass
