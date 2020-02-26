"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import block.Block
import event.Registry
import mod.ModMcpython


def register_block(registry, blockclass):
    if issubclass(blockclass, block.Block.Block):
        blockclass.on_register(block_registry)  # call event function
        name = blockclass.NAME
        block_registry.full_table[name] = blockclass
        block_registry.full_table[name.split(":")[-1]] = blockclass


block_registry = event.Registry.Registry("block", ["minecraft:block_registry"], injection_function=register_block)
block_registry.full_table = {}  # an table of localized & un-localized block names


def load():
    """
    loads all blocks that should be loaded, only the ones for blocks may be loaded somewhere else
    """
    from . import (BlockGrassBlock, BlockDirt, BlockCraftingTable, BlockChest, BlockEnderChest,
                   BlockShulkerBox, BlockCarpet, BlockFurnace, BlockBarrel, BlockCoralBlock)


mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:load", load, info="loading special blocks")


from . import (IFallingBlock, ILog)
from . import Blocks
