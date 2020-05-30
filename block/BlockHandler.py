"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import block.Block
import event.Registry
import mod.ModMcpython
import logger


def register_block(registry, blockclass):
    if issubclass(blockclass, block.Block.Block):
        blockclass.on_register(block_registry)  # call event function
        name = blockclass.NAME
        block_registry.full_table[name] = blockclass
        block_registry.full_table[name.split(":")[-1]] = blockclass
        instance = blockclass((0, 0, 0))
        if blockclass.SOLID is None:
            blockclass.SOLID = all(instance.face_solid.values())

        if blockclass.CONDUCTS_REDSTONE_POWER is None:
            blockclass.CONDUCTS_REDSTONE_POWER = blockclass.SOLID

        if blockclass.CAN_MOBS_SPAWN_ON is None:
            blockclass.CAN_MOBS_SPAWN_ON = blockclass.SOLID

        if not blockclass.ENABLE_RANDOM_TICKS:
            try:
                instance.on_random_update()
                logger.println("[WARN] block {} has not set ENABLE_RANDOM_TICKS, but the event function was changed!"
                               .format(blockclass.NAME))
                blockclass.ENABLE_RANDOM_TICKS = True
            except IOError:
                pass


block_registry = event.Registry.Registry("block", ["minecraft:block_registry"], injection_function=register_block)
block_registry.full_table = {}  # an table of localized & un-localized block names


def load():
    """
    loads all blocks that should be loaded, only the ones for blocks may be loaded somewhere else
    """
    from . import (BlockGrassBlock, BlockDirt, BlockCraftingTable, BlockChest, BlockEnderChest,
                   BlockShulkerBox, BlockCarpet, BlockFurnace, BlockBarrel, BlockCoralBlock, BlockFence, BlockWall)


mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:load", load, info="loading special blocks")


from . import (IFallingBlock, ILog)
from . import Blocks
