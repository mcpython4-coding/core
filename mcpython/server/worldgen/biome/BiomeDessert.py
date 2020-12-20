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
    DessertTempleFeature,
    DessertWellFeature,
    FossileFeature,
    PillagerOutpostDefinition,
    CactusFeature,
    PlantFeature,
    IOre,
)
from mcpython.server.worldgen.feature.village import VillageFeatureDefinition
from . import Biome
import mcpython.common.world.AbstractInterface
from mcpython.util.texture import hex_to_color


class Dessert(Biome.Biome):
    NAME = "minecraft:dessert"

    PASSIVE_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {
        "minecraft:rabbit": (4, (2, 3)),
    }
    HOSTILE_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {
        "minecraft:spider": (100, 4),
        "minecraft:skeleton": (100, 4),
        "minecraft:creeper": (100, 4),
        "minecraft:slime": (100, 4),
        "minecraft:enderman": (10, (1, 4)),
        "minecraft:witch": (5, 1),
        "minecraft:zombie": (19, 4),
        "minecraft:zombie_villager": (1, 1),
        "minecraft:husk": (80, 4),
    }
    AMBIENT_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {"minecraft:bat": (10, 8)}

    GRASS_COLOR = hex_to_color("bfb755")
    WATER_COLOR = hex_to_color("32a598")

    FEATURES = [
        DessertTempleFeature.DessertTempleFeature.as_feature_definition(
            10, "dessert_temples", (-100, 1)
        ),
        VillageFeatureDefinition.VillageFeatureDefinitionDessert.as_feature_definition(
            10, "villages", (-200, 1)
        ),
        DessertWellFeature.DessertWellFeature.as_feature_definition(
            10, "dessert_well", (-150, 1)
        ),
        FossileFeature.FossileFeatureOverworld.as_feature_definition(
            10, "fossiles", (-100, 1)
        ),
        PillagerOutpostDefinition.PillagerOutpostDefinition.as_feature_definition(
            10, "pillager_outposts", (-150, 1)
        ),
        PlantFeature.PlantFeature()
        .add_plant("minecraft:dead_bush", 10)
        .as_feature_definition(10, "plants", (10, 20)),
        CactusFeature.CactusFeature.as_feature_definition(5, "plants", (10, 20)),
        IOre.DefaultOreFeature.as_feature_definition(10, "ores"),
    ]

    @staticmethod
    def get_weight() -> int:
        return 20

    @staticmethod
    def get_height_range() -> typing.Tuple[int, int]:
        return mcpython.common.config.BIOME_HEIGHT_RANGE_MAP["minecraft:dessert"]

    @staticmethod
    def get_top_layer_height_range(
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.Tuple[int, int]:
        return 5, 9

    @staticmethod
    def get_top_layer_configuration(
        height: int,
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.List[str]:
        return ["minecraft:sandstone"] * 3 + ["minecraft:sand"] * (height - 3)


G.biome_handler.register(Dessert)
