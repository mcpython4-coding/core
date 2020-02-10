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
        name = blockclass.get_name()
        block_registry.get_attribute("blocks")[name] = block_registry.get_attribute("blocks")[name.split(":")[-1]] = \
            blockclass
        return
    registry.registered_objects.remove(blockclass)  # todo: when registry is seperated, remove this


block_registry = event.Registry.Registry("block", inject_base_classes=[block.Block.Block],
                                         injection_function=register_block)
block_registry.set_attribute("blocks", {})
block_registry.set_attribute("injectionclasses", {})


def load():
    """
    loads all blocks that should be loaded, only the ones for blocks may be loaded somewhere else
    """
    from . import (BlockGrassBlock, BlockDirt, BlockCraftingTable, BlockChest, BlockEnderChest,
                   BlockShulkerBox, BlockCarpet, BlockFurnace)


mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:load", load, info="loading special blocks")


from . import (IFallingBlock, ILog)
from . import Blocks
