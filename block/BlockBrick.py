"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk"""
import globals as G
from . import Block


@G.blockhandler
class BlockBricks(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:bricks"

    def get_tex_coords(self) -> list:
        return [(2, 0)] * 3

