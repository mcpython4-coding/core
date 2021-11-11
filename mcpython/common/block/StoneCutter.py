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
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython.util.enums import EnumSide, ToolType
from pyglet.window import key, mouse

from . import AbstractBlock
from .IHorizontalOrientableBlock import IHorizontalOrientableBlock


class StoneCutter(IHorizontalOrientableBlock):
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
    DEFAULT_FACE_SOLID = AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID

    def __init__(self):
        super().__init__()

        self.inventory = None  # todo: add stone cutter

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple, itemstack
    ):
        return False

    """ # open the inv when needed
        if button == mouse.RIGHT and not modifiers & (
            key.MOD_SHIFT | key.MOD_ALT | key.MOD_CTRL
        ):
            shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False"""

    def get_inventories(self):
        return [self.inventory]

    def get_provided_slot_lists(self, side):
        return self.inventory.slots, self.inventory.slots

    @classmethod
    def set_block_data(cls, item, block):
        if hasattr(item, "inventory"):
            block.inventory = item.inventory.copy()

    def on_request_item_for_block(self, itemstack):
        if (
            shared.window.keys[key.LCTRL]
            and shared.world.get_active_player().gamemode == 1
            and shared.window.mouse_pressing[mouse.MIDDLE]
        ):
            itemstack.item.inventory = self.inventory.copy()