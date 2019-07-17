"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
import globals as G
from . import Block


@G.blockhandler
class BlockGrassBlock(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:grass_block"

    def get_model_name(self):
        return "block/grass_block"

