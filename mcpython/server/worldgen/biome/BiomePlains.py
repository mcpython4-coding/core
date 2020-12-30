"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

from mcpython import shared as G
import mcpython.common.config
from mcpython.server.worldgen.feature import (
    OakTreeFeature,
    PillagerOutpostDefinition,
    PlantFeature,
    IOre,
)
from mcpython.server.worldgen.feature.village import VillageFeatureDefinition
from . import Biome


class Plains(Biome.Biome):
    NAME = "minecraft:plains"

    PASSIVE_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {
        "minecraft:sheep": (12, 4),
        "minecraft:pigs": (10, 4),
        "minecraft:chicken": (10, 4),
        "minecraft:cow": (8, 4),
        "minecraft:horse": (5, (2, 6)),
        "minecraft:donkey": (1, (1, 3)),
    }
    HOSTILE_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {
        "minecraft:spider": (100, 4),
        "minecraft:zombie": (95, 4),
        "minecraft:zombie_villager": (5, 1),
        "minecraft:skeleton": (100, 4),
        "minecraft:creeper": (100, 4),
        "minecraft:slime": (100, 4),
        "minecraft:enderman": (10, (1, 4)),
        "minecraft:witch": (5, 1),
    }
    AMBIENT_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {"minecraft:bat": (10, 8)}

    FEATURES = [
        OakTreeFeature.OakTreeNormalFeatureWithBees.as_feature_definition(
            1, "trees", (-3, 1)
        ),
        VillageFeatureDefinition.VillageFeatureDefinitionPlains.as_feature_definition(
            1, "villages", (-100, 1)
        ),
        PillagerOutpostDefinition.PillagerOutpostDefinition.as_feature_definition(
            1, "pillager_outposts", (-150, 1)
        ),
        PlantFeature.PlantFeature()
        .add_plant("minecraft:azure_bluet", 10)
        .add_plant("minecraft:oxeye_daisy", 10)
        .add_plant("minecraft:cornflower", 8)
        .add_plant("#minecraft:tulips", 1)
        .as_feature_definition(1, "flowers", (0, 3)),
        IOre.DefaultOreFeature.as_feature_definition(10, "ores"),
    ]

    @staticmethod
    def get_weight() -> int:
        return 20

    @staticmethod
    def get_height_range() -> typing.Tuple[int, int]:
        return mcpython.common.config.BIOME_HEIGHT_RANGE_MAP["minecraft:plains"]


# G.biome_handler.register(Plains)
