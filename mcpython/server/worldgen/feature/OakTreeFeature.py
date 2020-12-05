"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
from . import IFeature
import random
import math


class OakTreeNormalFeature:
    # todo: add big tree variant

    @staticmethod
    def place(dimension, x, y, z, heightrange=(3, 5)):
        height = random.randint(*heightrange)
        # place the logs
        for dy in range(height):
            dimension.get_chunk_for_position((x, y, z)).add_block(
                (x, y + dy, z), "minecraft:oak_log"
            )
        # place the leaves
        for dy in range(height - 2, height + 1):
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    chunk = dimension.get_chunk_for_position((x + dx, y, z + dz))
                    if (dx ** 2 + dz ** 2 + dy ** 2 / 4) ** (
                        1 / 2.25
                    ) < 3.5 and not chunk.is_position_blocked((x + dx, y + dy, z + dz)):
                        chunk.add_block(
                            (x + dx, y + dy, z + dz), "minecraft:oak_leaves"
                        )