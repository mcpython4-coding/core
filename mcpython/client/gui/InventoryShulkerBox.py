"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.client.gui.InventoryChest
import mcpython.common.item.IShulkerBoxLikeItem
import pyglet
import mcpython.common.event.EventHandler
from mcpython import shared as G


class InventoryShulkerBox(mcpython.client.gui.InventoryChest.InventoryChest):
    def create_slots(self) -> list:
        slots = super().create_slots()
        for slot in slots:
            slot.allowed_item_func = self.test_for_shulker
        return slots

    def test_for_shulker(self, itemstack):
        if itemstack.item and issubclass(
            type(itemstack.item),
            mcpython.common.item.IShulkerBoxLikeItem.IShulkerBoxLikeItem,
        ):
            return not itemstack.item.is_blocked_in(self)
        return True

    def on_activate(self):
        super().on_activate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )

    def on_deactivate(self):
        super().on_deactivate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            G.inventory_handler.hide(self)

    def update_shift_container(self):
        G.inventory_handler.shift_container.container_A = (
            G.world.get_active_player().inventories["main"].slots[:36]
        )
        G.inventory_handler.shift_container.container_B = self.slots
