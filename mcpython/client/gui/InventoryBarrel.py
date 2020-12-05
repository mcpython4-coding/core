"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.client.gui.Inventory
import mcpython.client.gui.Slot
import mcpython.common.container.ItemStack
import mcpython.client.gui.crafting.CraftingManager
import mcpython.client.gui.crafting.CraftingGridHelperInterface
import mcpython.common.container.ItemStack
import pyglet
import mcpython.common.event.EventHandler


class InventoryBarrel(mcpython.client.gui.Inventory.Inventory):
    """
    inventory class for chest
    """

    def __init__(self, block):
        super().__init__()
        self.block = block

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/blockinventorychest.json"

    def on_activate(self):
        super().on_activate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )
        self.block.opened = True
        self.block.face_state.update()

    def on_deactivate(self):
        super().on_deactivate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )
        self.block.opened = False
        self.block.face_state.update()

    def create_slots(self) -> list:
        # 3 rows of 9 slots of storage
        return [mcpython.client.gui.Slot.Slot() for _ in range(9 * 3)]

    def draw(self, hoveringslot=None):
        self.on_draw_background()
        x, y = self.get_position()
        if self.bgsprite:
            self.bgsprite.position = (x, y)
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()
        for slot in (
            G.world.get_active_player().inventories["main"].slots[:36] + self.slots
        ):
            slot.draw(x, y, hovering=slot == hoveringslot)
        self.on_draw_over_image()
        for slot in (
            G.world.get_active_player().inventories["main"].slots[:36] + self.slots
        ):
            slot.draw_label()
        self.on_draw_overlay()

    def get_interaction_slots(self):
        return G.world.get_active_player().inventories["main"].slots[:36] + self.slots

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            G.inventoryhandler.hide(self)

    def update_shift_container(self):
        G.inventoryhandler.shift_container.container_A = (
            G.world.get_active_player().inventories["main"].slots[:36]
        )
        G.inventoryhandler.shift_container.container_B = self.slots
