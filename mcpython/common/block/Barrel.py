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

from . import AbstractBlock


class Barrel(AbstractBlock.AbstractBlock):
    """
    Class for the Barrel-Block
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
        """
        Creates a new BlockBarrel-class
        """
        super().__init__()

        self.opened: bool = False  # if the barrel is open
        self.inventory = mcpython.client.gui.InventoryBarrel.InventoryBarrel(self)
        self.facing: str = "up"  # the direction the block faces to

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)
        self.inventory.write_to_network_buffer(buffer)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)
        self.inventory.read_from_network_buffer(buffer)

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
            elif dy > 0:
                self.facing = "down"
            elif dy < 0:
                self.facing = "up"

            if shared.IS_CLIENT:
                self.face_info.update()

            self.schedule_network_update()

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple, itemstack
    ):
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

        if "open" in state:
            self.opened = str(state["open"]).lower() == "true"

    def get_model_state(self) -> dict:
        return {
            "facing": self.facing.normal_name
            if not isinstance(self.facing, str)
            else self.facing,
            "open": str(self.opened).lower(),
        }

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

    def on_block_remove(self, reason):
        if shared.world.gamerule_handler.table["doTileDrops"].status.status:
            dimension = shared.world.get_dimension_by_name(self.dimension)

            for slot in self.inventory.slots:
                if slot.get_itemstack().is_empty(): continue

                dimension.spawn_itemstack_in_world(
                    slot.get_itemstack().copy(), self.position
                )
                slot.get_itemstack().clean()

        shared.inventory_handler.hide(self.inventory)
        del self.inventory
