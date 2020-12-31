"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.worldgen.feature.IFeature
import random

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
