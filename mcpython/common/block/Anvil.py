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

from . import IFallingBlock
from .IBlockContainerExposer import SimpleInventoryWrappingContainer


class AbstractAnvil(IFallingBlock.IFallingBlock, SimpleInventoryWrappingContainer):
    """
    Base class for all anvils
    Mods are allowed to implement this for their own anvils

    todo: add inventory & enable saving of it (with data fixer for it)
    """

    NETWORK_BUFFER_SERIALIZER_VERSION = 1

    HARDNESS = 5
    BLAST_RESISTANCE = 1200
    ASSIGNED_TOOLS = {ToolType.PICKAXE}

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_side("facing")
        .build()
    )

    BREAK_CHANCE = 0
    BREAKS_BLOCK_RESIST = 0
    BROKEN_BLOCK = None

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

    def __init__(self):
        super().__init__()

        self.opened: bool = False  # if the barrel is open
        self.inventory = None  # todo: add anvil inventory
        self.facing: str | EnumSide = "north"  # the direction the block faces to

        self.broken_count = 0

    async def on_block_added(self):
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

            await self.schedule_network_update()

    async def on_anvil_use(self):
        if random.random() < self.BREAK_CHANCE:
            self.broken_count += 1

            if self.broken_count >= self.BREAKS_BLOCK_RESIST:
                await self.dimension.add_block(self.position, self.BROKEN_BLOCK)

            await self.schedule_network_update()

    async def on_block_remove(self, reason):
        return

        # if shared.world.gamerule_handler.table["doTileDrops"].status.status:
        #     for slot in self.inventory.slots:
        #         await shared.world.get_active_player().pick_up_item(
        #             slot.itemstack.copy()
        #         )
        #         slot.itemstack.clean()
        #
        # await shared.inventory_handler.hide(self.inventory)
        # del self.inventory

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        # await self.inventory.write_to_network_buffer(buffer)
        buffer.write_int(self.broken_count)
        buffer.write_int(EnumSide[self.facing.upper()].index)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        # await self.inventory.read_from_network_buffer(buffer)
        self.broken_count = buffer.read_int()
        self.facing = EnumSide.by_index(buffer.read_int()).normal_name

    async def set_model_state(self, state: dict):
        if "facing" in state:
            face = state["facing"]

            if type(face) == str:
                self.facing = face
            else:
                self.facing = face.normal_name

    def get_model_state(self) -> dict:
        return {
            "facing": self.facing.normal_name
            if not isinstance(self.facing, str)
            else self.facing,
        }

    async def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple, itemstack
    ):
        return False

    """ # open the inv when needed
        if button == mouse.RIGHT and not modifiers & (
            key.MOD_SHIFT | key.MOD_ALT | key.MOD_CTRL
        ):
            await shared.inventory_handler.show(self.inventory)
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

    async def on_request_item_for_block(self, itemstack):
        if (
            shared.window.keys[key.LCTRL]
            and shared.world.get_active_player().gamemode == 1
            and shared.window.mouse_pressing[mouse.MIDDLE]
        ):
            itemstack.item.inventory = self.inventory.copy()


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
