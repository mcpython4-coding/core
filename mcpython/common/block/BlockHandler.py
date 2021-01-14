"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
import mcpython.common.block.AbstractBlock
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython
from mcpython.common.block.AbstractBlock import AbstractBlock
import mcpython.common.data.tags.TagGroup


tag_holder = mcpython.common.data.tags.TagGroup.TagTargetHolder("blocks")


def register_block(registry, cls):
    if issubclass(cls, mcpython.common.block.AbstractBlock.AbstractBlock):
        tag_holder.register_class(cls)

        cls.on_register(block_registry)  # call event function
        name = cls.NAME
        block_registry.full_table[name] = cls
        block_registry.full_table[name.split(":")[-1]] = cls
        instance = cls()
        if cls.IS_SOLID is None:
            cls.IS_SOLID = all(instance.face_solid.values())

        if cls.CAN_CONDUCT_REDSTONE_POWER is None:
            cls.CAN_CONDUCT_REDSTONE_POWER = cls.IS_SOLID

        if cls.CAN_MOBS_SPAWN_ON is None:
            cls.CAN_MOBS_SPAWN_ON = cls.IS_SOLID


block_registry = mcpython.common.event.Registry.Registry(
    "minecraft:block",
    ["minecraft:block_registry"],
    "stage:block:load",
    injection_function=register_block,
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
