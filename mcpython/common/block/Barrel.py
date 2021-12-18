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
import mcpython.client.gui.InventoryBarrel
import mcpython.common.block.PossibleBlockStateBuilder
import mcpython.util.enums
import pyglet
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from pyglet.window import key, mouse

from .IAllDirectionOrientableBlock import IAllDirectionOrientableBlock


class Barrel(IAllDirectionOrientableBlock):
    """
    Class for the Barrel-Block
    Barrels are container blocks, with one front face
    """

    NAME = "minecraft:barrel"

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_bool("open")
        .add_comby_side("facing")
        .build()
    )

    HARDNESS = BLAST_RESISTANCE = 2.5
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.AXE}

    def __init__(self):
        super().__init__()

        # if the barrel is open
        self.opened: bool = False

        # the inventory instance
        self.inventory = mcpython.client.gui.InventoryBarrel.InventoryBarrel(self)

    async def on_block_added(self):
        await self.inventory.init()
        await self.inventory.reload_config()

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)
        await self.inventory.write_to_network_buffer(buffer)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)
        await self.inventory.read_from_network_buffer(buffer)

    async def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple, itemstack
    ):
        # open the inv when needed
        if button == mouse.RIGHT and not modifiers & (
            key.MOD_SHIFT | key.MOD_ALT | key.MOD_CTRL
        ):
            await shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    def get_provided_slot_lists(self, side):
        return self.inventory.slots, self.inventory.slots

    def set_model_state(self, state: dict):
        super().set_model_state(state)

        if "open" in state:
            self.opened = str(state["open"]).lower() == "true"

    def get_model_state(self) -> dict:
        return super().get_model_state() | {"open": str(self.opened).lower()}

    @classmethod
    def set_block_data(cls, item, block):
        if hasattr(item, "inventory"):
            block.inventory = item.inventory.copy()

    def on_request_item_for_block(self, itemstack):
        if (
            shared.window.keys[pyglet.window.key.LCTRL]
            and shared.world.get_active_player().gamemode == 1
            and shared.window.mouse_pressing[pyglet.window.mouse.MIDDLE]
        ):
            itemstack.item.inventory = self.inventory.copy()

    async def on_block_remove(self, reason):
        if shared.world.gamerule_handler.table["doTileDrops"].status.status:
            dimension = shared.world.get_dimension_by_name(self.dimension)

            for slot in self.inventory.slots:
                if slot.get_itemstack().is_empty():
                    continue

                dimension.spawn_itemstack_in_world(
                    slot.get_itemstack().copy(), self.position
                )
                slot.get_itemstack().clean()

        await shared.inventory_handler.hide(self.inventory)
        del self.inventory
