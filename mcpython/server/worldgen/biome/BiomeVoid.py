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

from mcpython import shared
import mcpython.common.config
from . import Biome
import mcpython.common.world.AbstractInterface


class Void(Biome.Biome):
    NAME = "minecraft:void"

    @staticmethod
    def get_weight() -> int:
        return 1

    @staticmethod
    def get_height_range() -> typing.Tuple[int, int]:
        return 0, 0

    @staticmethod
    def get_top_layer_height_range(
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.Tuple[int, int]:
        return 0, 0

    @staticmethod
    def get_top_layer_configuration(
        height: int,
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.List[str]:
        return []


shared.biome_handler.register(Void)
