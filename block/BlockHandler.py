"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
import globals as G
import block.Block


class BlockHandler:
    def __init__(self):
        self.blocks = {}

    def register(self, obj):
        if issubclass(obj, block.Block.Block):
            name = obj.get_name()
            self.blocks[name] = self.blocks[name.split(":")[-1]] = obj
            if obj.is_optainable_by_player():
                G.window.inventory.append(obj.get_name())
            if obj.is_part_of_pyramids():
                G.model.pyramid_parts.append(obj.get_name())
        else:
            raise ValueError("can only cast "+str(block.Block.Block)+"-subclasses to valid blocks")

    def __call__(self, obj):
        self.register(obj)


handler = G.blockhandler = BlockHandler()


def load():
    from . import (BlockGrassBlock, BlockSand, BlockBrick, BlockStone, BlockDirt)

