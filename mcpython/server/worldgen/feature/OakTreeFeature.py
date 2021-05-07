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
class OakTreeNormalFeature(IFeature.IFeature):
    NAME = "minecraft:oak_tree_feature"
    # todo: add big tree variant

    @classmethod
    def place(cls, dimension, x, y, z, config):
        height_range = config.setdefault("height_range", (3, 6))
        height = random.randint(*height_range)

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

    @classmethod
    def place_array(cls, array, x: int, y: int, z: int, config):
        height_range = config.setdefault("height_range", (3, 6))
        height = random.randint(*height_range)

        # place the logs
        for dy in range(height):
            array.schedule_block_add((x, y + dy, z), "minecraft:oak_log")

        # place the leaves
        for dy in range(height - 2, height + 1):
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    if (dx ** 2 + dz ** 2 + dy ** 2 / 4) ** (
                        1 / 2.25
                    ) < 3.5 and array.get_block((x + dx, y + dy, z + dz)) is None:
                        array.schedule_block_add(
                            (x + dx, y + dy, z + dz), "minecraft:oak_leaves"
                        )


@shared.registry
class OakTreeNormalFeatureWithBees(OakTreeNormalFeature):
    NAME = "minecraft:oak_tree_feature_bees"
