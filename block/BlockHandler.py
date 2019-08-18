"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block


class BlockHandler:
    def __init__(self):
        self.blocks = {}
        self.blockclasses = []
        self.used_models = []

    def register(self, obj):
        if issubclass(obj, block.Block.Block):
            self.blockclasses.append(obj)
            name = obj.get_name()
            self.blocks[name] = self.blocks[name.split(":")[-1]] = obj
            self.used_models += obj.get_used_models()
            self.used_models = list(dict.fromkeys(self.used_models))
        else:
            raise ValueError("can only cast "+str(block.Block.Block)+"-subclasses to valid blocks")

    def __call__(self, obj):
        self.register(obj)


handler = G.blockhandler = BlockHandler()


def load():
    from . import (BlockGrassBlock, BlockSand, BlockBrick, BlockStone, BlockDirt, BlockBedrock, BlockCobbleStone,
                   BlockCoalOre, BlockIronOre, BlockGoldOre, BlockEmeraldOre, BlockRedstoneOre, BlockDiamondOre,
                   BlockLapisOre)

