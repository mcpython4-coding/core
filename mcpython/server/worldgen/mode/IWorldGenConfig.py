"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
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
            noises[0].noise4d(
                x / config.size, z / config.size, x * z / config.size ** 2,
                noises[1].noise3d(
                    x / (config.size * 100), z / (config.size * 100),
                    noises[2].noise3d(
                        x / (config.size * 100) + z / 1000000, z / (config.size * 100) + x / 1000000,
                        len(landmass) / 100000
                    ) / 10000
                )
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

    GENERATES_START_CHEST = False

    @classmethod
    def on_chunk_generation_finished(cls, chunk):
        pass
