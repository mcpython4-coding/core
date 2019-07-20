"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
from . import Block


@G.blockhandler
class BlockCobbleStone(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:cobblestone"

    def get_model_name(self):
        return "block/cobblestone"
