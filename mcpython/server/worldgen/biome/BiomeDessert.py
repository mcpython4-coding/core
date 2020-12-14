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
import mcpython.server.worldgen.feature.OakTreeFeature
from . import Biome
import mcpython.common.world.AbstractInterface


class Dessert(Biome.Biome):
    NAME = "minecraft:dessert"

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
