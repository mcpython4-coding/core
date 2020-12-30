"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.event.Registry
import mcpython.server.worldgen.WorldGenerationTaskArrays


class IFeatureSpawnPoint:
    @classmethod
    def select(cls, x, z, gen_height, biome) -> int:
        raise NotImplementedError()


class TopLayerSpawnPoint(IFeatureSpawnPoint):
    @classmethod
    def select(cls, x, z, gen_height, biome) -> int:
        return gen_height + 1


class FeatureDefinition:
    """
    Class holding generation rules and config for an IFeature-class.
    """

    def __init__(
        self,
        feature: typing.Type["IFeature"],
        weight: int,
        group: str,
        group_spawn_count: typing.Union[int, typing.Tuple[int, int]] = 1,
        point: typing.Type[IFeatureSpawnPoint] = TopLayerSpawnPoint,
        config=None,
    ):
        self.feature = feature
        self.weight = weight
        self.group = group
        self.group_spawn_count = group_spawn_count
        self.spawn_point = point
        self.config = {} if config is None else config


class IFeature(mcpython.common.event.Registry.IRegistryContent):
    TYPE = "minecraft:generation_feature"

    @classmethod
    def place(cls, dimension, x: int, y: int, z: int, config):
        pass

    @classmethod
    def place_array(
        cls,
        array: mcpython.server.worldgen.WorldGenerationTaskArrays.IWorldGenerationTaskHandlerReference,
        x: int,
        y: int,
        z: int,
        config,
    ):
        pass

    @classmethod
    def as_feature_definition(
        cls,
        weight: int,
        group: str,
        group_spawn_count: typing.Union[int, typing.Tuple[int, int]] = 1,
        point: typing.Type[IFeatureSpawnPoint] = TopLayerSpawnPoint,
        config=None,
    ) -> FeatureDefinition:
        return FeatureDefinition(cls, weight, group, group_spawn_count, point, config)

    @classmethod
    def as_feature_definition_with_custom_config(
        cls,
        weight: int,
        group: str,
        custom_config: dict,
        group_spawn_count: typing.Union[int, typing.Tuple[int, int]] = 1,
        point: typing.Type[IFeatureSpawnPoint] = TopLayerSpawnPoint,
        config=None,
    ) -> FeatureDefinition:
        pass
