"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
import globals as G
from . import Block


@G.blockhandler
class BlockDirt(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:dirt"

    def get_tex_coords(self) -> list:
        return [(0, 1)] * 3

