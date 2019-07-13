"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk"""
import globals as G
from . import Block


@G.blockhandler
class BlockStone(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stone"

    def get_tex_coords(self) -> list:
        return [(2, 1)] * 3

    def is_brakeable(self) -> bool:
        return False

    @staticmethod
    def is_optainable_by_player() -> bool:
        return False

    @staticmethod
    def is_part_of_pyramids() -> bool:
        return False

