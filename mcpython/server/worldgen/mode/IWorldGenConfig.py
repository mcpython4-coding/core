"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.data.serializer.DataSerializationManager
import mcpython.common.data.serializer.worldgen.WorldGenerationMode
import mcpython.engine.world.AbstractInterface
import mcpython.server.worldgen.WorldGenerationTaskArrays
from mcpython import shared


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
        return (self.biome_name,)


class DefaultBiomeSource(IBiomeSource):
    """
    The default biome source
    """

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


class IWorldGenConfig(
    mcpython.common.data.serializer.DataSerializationManager.ISerializeAble
):
    SERIALIZER = (
        mcpython.common.data.serializer.worldgen.WorldGenerationMode.WorldGenerationModeSerializer
    )

    NAME = None
    DIMENSION = None
    DISPLAY_NAME = None

    BIOMES = []
    BIOME_SOURCE: IBiomeSource = SingleBiomeSource("minecraft:void")

    LANDMASSES = []
    LAYERS = []

    GENERATES_START_CHEST = False

    # A lazy mcpython.common.state.worldgen.AbstractWorldGeneration.AbstractState for usage for configuration
    # todo: use this API and display it correctly
    # todo: add serialization config
    # todo: store configured object for later usage
    CONFIGURATION_STATE_INSTANCE = None

    @classmethod
    def on_chunk_prepare_generation(
        cls,
        chunk: mcpython.engine.world.AbstractInterface.IChunk,
        array: mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference,
    ):
        pass

    @classmethod
    def on_chunk_generation_finished(
        cls, chunk: mcpython.engine.world.AbstractInterface.IChunk
    ):
        pass


mcpython.common.data.serializer.worldgen.WorldGenerationMode.WorldGenerationModeSerializer.BIOME_SOURCES.update(
    {
        "minecraft:single_biome": SingleBiomeSource,
        "minecraft:default_biome": DefaultBiomeSource,
    }
)
