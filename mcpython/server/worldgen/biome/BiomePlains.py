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


class Plains(Biome.Biome):
    NAME = "minecraft:plains"

    @staticmethod
    def get_weight() -> int:
        return 20

    @staticmethod
    def get_height_range() -> typing.Tuple[int, int]:
        return mcpython.common.config.BIOME_HEIGHT_RANGE_MAP["minecraft:plains"]

    @staticmethod
    def get_trees() -> list:
        return [
            (mcpython.server.worldgen.feature.OakTreeFeature.OakTreeNormalFeature, 600)
        ]


G.biome_handler.register(Plains)
