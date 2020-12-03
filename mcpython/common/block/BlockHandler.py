"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
import mcpython.common.block.AbstractBlock
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython
from mcpython.common.block.AbstractBlock import AbstractBlock


def register_block(registry, blockclass):
    if issubclass(blockclass, mcpython.common.block.AbstractBlock.AbstractBlock):
        blockclass.on_register(block_registry)  # call event function
        name = blockclass.NAME
        block_registry.full_table[name] = blockclass
        block_registry.full_table[name.split(":")[-1]] = blockclass
        instance = blockclass()
        if blockclass.IS_SOLID is None:
            blockclass.IS_SOLID = all(instance.face_solid.values())

        if blockclass.CAN_CONDUCT_REDSTONE_POWER is None:
            blockclass.CAN_CONDUCT_REDSTONE_POWER = blockclass.IS_SOLID

        if blockclass.CAN_MOBS_SPAWN_ON is None:
            blockclass.CAN_MOBS_SPAWN_ON = blockclass.IS_SOLID

        if not blockclass.ENABLE_RANDOM_TICKS:

            # check for functional identical parts
            if instance.on_random_update.__code__ != AbstractBlock.on_random_update.__code__:
                logger.println(
                    "[WARN] block '{}' has not set ENABLE_RANDOM_TICKS, but the event function was changed "
                    "from {} to {}!".format(
                        blockclass.NAME,
                        blockclass.on_random_update,
                        AbstractBlock.on_random_update,
                    )
                )
                blockclass.ENABLE_RANDOM_TICKS = True


block_registry = mcpython.common.event.Registry.Registry(
    "block", ["minecraft:block_registry"], "stage:block:load", injection_function=register_block
)
block_registry.full_table = {}  # an table of localized & un-localized block names


def load():
    """
    loads all blocks that should be loaded, only the ones for blocks may be loaded somewhere else
    """
    from . import (
        BlockGrassBlock,
        BlockDirt,
        BlockCraftingTable,
        BlockChest,
        BlockEnderChest,
        BlockNetherPortal,
        BlockShulkerBox,
        BlockCarpet,
        BlockFurnace,
        BlockBarrel,
        BlockCoralBlock,
        BlockFence,
        BlockWall,
    )


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:block:load", load, info="loading special blocks"
)


from . import IFallingBlock, ILog
from . import Blocks
