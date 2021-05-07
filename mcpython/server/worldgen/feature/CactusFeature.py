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

import mcpython.server.worldgen.feature.IFeature
from mcpython import shared


@shared.registry
class CactusFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:cactus_feature"

    @classmethod
    def place(cls, dimension, x: int, y: int, z: int, config):
        for dy in range(0, random.randint(1, 3)):
            dimension.add_block((x, y + dy, z), "minecraft:cactus")

    @classmethod
    def place_array(cls, array, x: int, y: int, z: int, config):
        for dy in range(0, random.randint(1, 3)):
            array.schedule_block_add((x, y + dy, z), "minecraft:cactus")
