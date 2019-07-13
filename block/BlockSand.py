"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk"""
import globals as G
from . import Block


@G.blockhandler
class BlockSand(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:sand"

    def get_tex_coords(self) -> list:
        return [(1, 1)] * 3
