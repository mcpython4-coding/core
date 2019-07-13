"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk"""
import globals as G
from . import Block


@G.blockhandler
class BlockGrassBlock(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:grass_block"

    def get_tex_coords(self) -> list:
        return [(1, 0), (0, 1), (0, 0)]

