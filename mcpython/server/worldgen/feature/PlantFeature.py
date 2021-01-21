"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.server.worldgen.feature.IFeature
from mcpython import shared


@shared.registry
class PlantFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:plant_feature"

    def __init__(self):
        self.plants = []

    def add_plant(self, plant: str, weight: int):
        self.plants.append((plant, weight))
        return self

    @classmethod
    def as_feature_definition_with_custom_config(
        cls,
        weight: int,
        group: str,
        custom_config: dict,
        group_spawn_count: typing.Union[int, typing.Tuple[int, int]] = 1,
        point: typing.Type[
            mcpython.server.worldgen.feature.IFeature.IFeatureSpawnPoint
        ] = mcpython.server.worldgen.feature.IFeature.TopLayerSpawnPoint,
        config=None,
    ) -> mcpython.server.worldgen.feature.IFeature.FeatureDefinition:
        instance = cls()
        for key in custom_config:
            instance.add_plant(key, custom_config[key])
        return instance.as_feature_definition()
