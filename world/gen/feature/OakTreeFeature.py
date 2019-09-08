"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import IFeature
import random
import math


class OakTreeNormalFeature:
    @staticmethod
    def place(dimension, x, y, z, heightrange=(3, 5)):
        height = random.randint(*heightrange)
        # place the logs
        for dy in range(height):
            dimension.get_chunk_for_position((x, y, z)).add_add_block_gen_task((x, y+dy, z), "minecraft:oak_log")
        # place the leaves
        for dy in range(height-2, height+1):
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    chunk = dimension.get_chunk_for_position((x+dx, y, z+dz))
                    if (dx ** 2 + dz ** 2 + dy ** 2 / 4) ** (1/2.25) < 3.5 and not \
                            chunk.is_position_blocked((x+dx, y+dy, z+dz)):
                        chunk.add_add_block_gen_task((x+dx, y+dy, z+dz), "minecraft:oak_leaves")

