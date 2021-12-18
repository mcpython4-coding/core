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
import random

import mcpython.common.block.PossibleBlockStateBuilder
from mcpython import shared
from mcpython.common.container.crafting.IRecipeUser import IRecipeUser
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython.util.enums import EnumSide, ToolType
from pyglet.window import key, mouse

from . import AbstractBlock
from .IHorizontalOrientableBlock import IHorizontalOrientableBlock

if shared.IS_CLIENT:
    from mcpython.client.gui.StoneCutterContainerRenderer import (
        StoneCutterContainerRenderer,
    )


class StoneCutter(IHorizontalOrientableBlock, IRecipeUser):
    """
    Class for the stone cutter block
    """

    NAME = "minecraft:stonecutter"

    HARDNESS = BLAST_RESISTANCE = 3.5
    ASSIGNED_TOOLS = {ToolType.PICKAXE}
    MINIMUM_TOOL_LEVEL = 1

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_side("facing")
        .build()
    )

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

    INVENTORY = None

    def __init__(self):
        super().__init__()

        if StoneCutter.INVENTORY is None and shared.IS_CLIENT:
            self.inventory = StoneCutter.INVENTORY = StoneCutterContainerRenderer()
        else:
            self.inventory = StoneCutter.INVENTORY

    async def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple, itemstack
    ):
        if button == mouse.RIGHT and not modifiers & (
            key.MOD_SHIFT | key.MOD_ALT | key.MOD_CTRL
        ):
            await shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False

    async def on_block_added(self):
        await super().on_block_added()
        await self.inventory.init()
        await self.inventory.reload_config()

    async def on_block_remove(self, reason):
        await shared.inventory_handler.hide(self.inventory)
        self.inventory = None

    def get_inventories(self):
        return [self.inventory]

    @classmethod
    def set_block_data(cls, item, block):
        if hasattr(item, "inventory"):
            block.inventory = item.inventory.copy()
