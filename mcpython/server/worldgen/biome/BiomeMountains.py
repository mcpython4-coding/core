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

import mcpython.common.config
from mcpython import shared
from mcpython.server.worldgen.feature import IOre, SpruceTreeFeature

from . import Biome


class Plains(Biome.Biome):
    NAME = "minecraft:mountains"

    PASSIVE_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {
        "minecraft:sheep": (12, 4),
        "minecraft:pigs": (10, 4),
        "minecraft:chicken": (10, 4),
        "minecraft:cow": (8, 4),
        "minecraft:llama": (5, (4, 6)),
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
        SpruceTreeFeature.SpruceTreeNormalFeature.as_feature_definition(
            10, "trees", (4, 10)
        ),
        IOre.DefaultOreFeature.as_feature_definition(10, "ores"),
        IOre.DefaultEmeraldFeature.as_feature_definition(10, "ores"),
        IOre.DefaultInfestedStoneFeature.as_feature_definition(
            10, "infested_stone", (2, 5)
        ),
    ]

    @staticmethod
    def get_weight() -> int:
        return 20

    @staticmethod
    def get_height_range() -> typing.Tuple[int, int]:
        return mcpython.common.config.BIOME_HEIGHT_RANGE_MAP["minecraft:mountains"]


shared.biome_handler.register(Plains)
