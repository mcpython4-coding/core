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
import mcpython.util.enums
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from pyglet.window import key, mouse

from . import AbstractBlock, IFallingBlock


class AbstractAnvil(IFallingBlock.IFallingBlock):
    """
    Base class for all anvils
    Mods are allowed to implement this for their own anvils
    """

    HARDNESS = 5
    BLAST_RESISTANCE = 1200
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.PICKAXE]

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_side("facing")
        .build()
    )

    BREAK_CHANCE = 0
    BREAKS_BLOCK_RESIST = 0
    BROKEN_BLOCK = None

    SOLID = False
    DEFAULT_FACE_SOLID = AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID

    def __init__(self):
        super().__init__()

        self.opened: bool = False  # if the barrel is open
        self.inventory = None  # todo: add anvil inventory
        self.facing: str = "north"  # the direction the block faces to

        self.broken_count = 0

    def on_block_added(self):
        # only if this is set, decode it
        if self.set_to is not None:
            dx, dy, dz = tuple([self.position[i] - self.set_to[i] for i in range(3)])
            if dx > 0:
                self.facing = "west"
            elif dz > 0:
                self.facing = "north"
            elif dx < 0:
                self.facing = "east"
            elif dz < 0:
                self.facing = "south"

            if shared.IS_CLIENT:
                self.face_info.update()

    def on_anvil_use(self):
        if random.random() < self.BREAK_CHANCE:
            self.broken_count += 1

            if self.broken_count >= self.BREAKS_BLOCK_RESIST:
                self.dimension.add_block(self.position, self.BROKEN_BLOCK)

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)
        self.inventory.write_to_network_buffer(buffer)
        buffer.write_int(self.broken_count)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)
        self.inventory.read_from_network_buffer(buffer)
        self.broken_count = buffer.read_int()

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        return False

        # open the inv when needed
        if button == mouse.RIGHT and not modifiers & (
            key.MOD_SHIFT | key.MOD_ALT | key.MOD_CTRL
        ):
            shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    def get_provided_slot_lists(self, side):
        return self.inventory.slots, self.inventory.slots

    def set_model_state(self, state: dict):
        if "facing" in state:
            face = state["facing"]
            if type(face) == str:
                self.facing = mcpython.util.enums.EnumSide[face.upper()]
            else:
                self.facing = face

    def get_model_state(self) -> dict:
        return {
            "facing": self.facing.normal_name
            if not isinstance(self.facing, str)
            else self.facing,
        }

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

    def on_block_remove(self, reason):
        return

        if shared.world.gamerule_handler.table["doTileDrops"].status.status:
            for slot in self.inventory.slots:
                shared.world.get_active_player().pick_up_item(slot.itemstack.copy())
                slot.itemstack.clean()

        shared.inventory_handler.hide(self.inventory)
        del self.inventory


class Anvil(AbstractAnvil):
    NAME = "minecraft:anvil"

    BREAK_CHANCE = 0.12
    BROKEN_BLOCK = "minecraft:chipped_anvil"


class ChippedAnvil(AbstractAnvil):
    NAME = "minecraft:chipped_anvil"

    BREAK_CHANCE = 0.12
    BROKEN_BLOCK = "minecraft:damaged_anvil"


class DamagedAnvil(AbstractAnvil):
    NAME = "minecraft:damaged_anvil"

    BREAK_CHANCE = 0.12
