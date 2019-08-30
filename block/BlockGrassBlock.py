"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block


@G.blockhandler
class BlockGrassBlock(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:grass_block"

    def get_model_name(self):
        return "block/grass_block"

