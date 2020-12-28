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
import mcpython.common.world.AbstractInterface
import mcpython.server.worldgen.WorldGenerationTaskArrays
import mcpython.common.data.DataSerializerHandler
import mcpython.common.data.worldgen.WorldGenerationMode


class IBiomeSource:
    def get_biome_at(self, x, z, noises, landmass, config, temperature) -> str:
        raise NotImplementedError()

    def get_creation_args(self) -> typing.List:
        raise NotImplementedError()


class SingleBiomeSource(IBiomeSource):
    def __init__(self, biome_name: str):
        self.biome_name = biome_name

    def get_biome_at(self, x, z, noises, landmass, config, temperature) -> str:
        return self.biome_name

    def get_creation_args(self) -> typing.Tuple:
        return self.biome_name,


class DefaultBiomeSource(IBiomeSource):
    @classmethod
    def get_biome_at(cls, x, z, noises, landmass, config, temperature) -> str:
        v = (
            noises[0].calculate_position(
                (
                    x,
                    z,
                    x * z,
                    noises[1].calculate_position(
                        (
                            x / 100,
                            z / 100,
                            noises[2].calculate_position(
                                (
                                    x / 100 + z / 1000000,
                                    z / 100 + x / 1000000,
                                    len(landmass) / 100000,
                                    0,
                                )
                            )
                            / 10000,
                            0,
                        )
                    ),
                )
            )
            * 0.5
            + 0.5
        )
        return shared.biome_handler.get_biome_at(
            landmass, v, temperature, config.world_generator_config.BIOMES
        )

    @classmethod
    def get_creation_args(cls) -> typing.Tuple:
        return tuple()


class IWorldGenConfig(mcpython.common.data.DataSerializerHandler.ISerializeAble):
    SERIALIZER = (
        mcpython.common.data.worldgen.WorldGenerationMode.WorldGenerationModeSerializer
    )

    NAME = None
    DIMENSION = None
    DISPLAY_NAME = None

    BIOMES = []
    BIOME_SOURCE: typing.Type[IBiomeSource] = SingleBiomeSource("minecraft:void")

    LANDMASSES = []
    LAYERS = []

    GENERATES_START_CHEST = False

    @classmethod
    def on_chunk_prepare_generation(
        cls,
        chunk: mcpython.common.world.AbstractInterface.IChunk,
        array: mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference,
    ):
        pass

    @classmethod
    def on_chunk_generation_finished(
        cls, chunk: mcpython.common.world.AbstractInterface.IChunk
    ):
        pass


mcpython.common.data.worldgen.WorldGenerationMode.WorldGenerationModeSerializer.BIOME_SOURCES.update(
    {
        "minecraft:single_biome": SingleBiomeSource,
        "minecraft:default_biome": DefaultBiomeSource,
    }
)
