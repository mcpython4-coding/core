"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.block.AbstractBlock
import mcpython.common.data.serializer.tags.TagGroup
import mcpython.common.event.Registry
from mcpython import shared
from mcpython.common.block.AbstractBlock import AbstractBlock
from mcpython.engine import logger

tag_holder = mcpython.common.data.serializer.tags.TagGroup.TagTargetHolder("blocks")


def register_block(registry, cls):
    if issubclass(cls, mcpython.common.block.AbstractBlock.AbstractBlock):
        tag_holder.register_class(cls)

        cls.on_register(block_registry)  # call event function
        name = cls.NAME
        block_registry.full_table[name] = cls
        block_registry.full_table[name.split(":")[-1]] = cls
        instance = cls()
        if cls.IS_SOLID is None:
            cls.IS_SOLID = all(instance.face_solid)

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
        Anvil,
        Barrel,
        Carpet,
        Chest,
        CoralBlocks,
        CraftingTable,
        Dirt,
        EnderChest,
        Fence,
        Furnace,
        GrassBlock,
        NetherPortal,
        NewBlocks,
        Rails,
        RedstoneWire,
        ShulkerBox,
        Walls,
    )

    block_registry.register(Anvil.Anvil)
    block_registry.register(Anvil.ChippedAnvil)
    block_registry.register(Anvil.DamagedAnvil)
    block_registry.register(GrassBlock.GrassBlock)
    block_registry.register(Dirt.Dirt)
    block_registry.register(CraftingTable.CraftingTable)
    block_registry.register(Chest.Chest)
    block_registry.register(EnderChest.EnderChest)
    block_registry.register(NetherPortal.NetherPortalBlock)
    block_registry.register(Furnace.Furnace)
    block_registry.register(Furnace.BlastFurnace)
    block_registry.register(Furnace.Smoker)
    block_registry.register(Barrel.Barrel)
    block_registry.register(CoralBlocks.BubbleCoralBlock)
    block_registry.register(CoralBlocks.BrainCoralBlock)
    block_registry.register(CoralBlocks.FireCoralBlock)
    block_registry.register(CoralBlocks.HornCoralBlock)
    block_registry.register(CoralBlocks.TubeCoralBlock)
    block_registry.register(Fence.OakFence)
    block_registry.register(Fence.SpruceFence)
    block_registry.register(Fence.BirchFence)
    block_registry.register(Fence.JungleFence)
    block_registry.register(Fence.CrimsonFence)
    block_registry.register(Fence.DarkOakFence)
    block_registry.register(Fence.NetherBrickFence)
    block_registry.register(Fence.WarpedFence)
    block_registry.register(Fence.AcaciaFence)
    block_registry.register(RedstoneWire.RedstoneWire)
    block_registry.register(Rails.ActivatorRail)

    Carpet.load()
    CoralBlocks.load()
    ShulkerBox.load()
    Walls.load()


if not shared.IS_TEST_ENV:
    import mcpython.common.mod.ModMcpython

    mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
        "stage:block:factory:prepare", load, info="loading special blocks"
    )

    from . import Blocks, IFallingBlock, ILog
