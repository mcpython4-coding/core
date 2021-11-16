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
import random

from mcpython import shared

from . import IFeature


@shared.registry
class JunglePyramid(IFeature.IFeature):
    NAME = "minecraft:jungle_pyramid"

    @classmethod
    def place(cls, dimension, x, y, z, config):
        pass

    @classmethod
    def place_array(cls, array, x: int, y: int, z: int, config):
        pass
