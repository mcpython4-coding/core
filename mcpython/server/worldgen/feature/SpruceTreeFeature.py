"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from . import IFeature
import random


@shared.registry
class SpruceTreeNormalFeature(IFeature.IFeature):
    NAME = "minecraft:spruce_tree_feature"

    # todo: implement real

    @classmethod
    def place(cls, dimension, x, y, z, config):
        height_range = config.setdefault("height_range", (5, 10))
        height = random.randint(*height_range)
        # place the logs
        for dy in range(height):
            dimension.get_chunk_for_position((x, y, z)).add_block(
                (x, y + dy, z), "minecraft:spruce_log"
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
                            (x + dx, y + dy, z + dz), "minecraft:spruce_leaves"
                        )

    @classmethod
    def place_array(cls, array, x: int, y: int, z: int, config):
        height_range = config.setdefault("height_range", (5, 10))
        height = random.randint(*height_range)
        # place the logs
        for dy in range(height):
            array.schedule_block_add((x, y + dy, z), "minecraft:spruce_log")
        # place the leaves
        for dy in range(height - 2, height + 1):
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    if (dx ** 2 + dz ** 2 + dy ** 2 / 4) ** (
                        1 / 2.25
                    ) < 3.5 and array.get_block((x + dx, y + dy, z + dz)) is None:
                        array.schedule_block_add(
                            (x + dx, y + dy, z + dz), "minecraft:spruce_leaves"
                        )
