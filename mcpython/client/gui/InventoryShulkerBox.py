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
import mcpython.client.gui.InventoryChest
import pyglet
import mcpython.common.event.EventHandler
from mcpython import shared as G


class InventoryShulkerBox(mcpython.client.gui.InventoryChest.InventoryChest):
    def create_slots(self) -> list:
        slots = super().create_slots()
        for slot in slots:
            slot.disallowed_item_tags = ["#minecraft:shulkerbox_like_items"]
        return slots

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
            G.world.get_active_player().inventory_main.slots[:36]
        )
        G.inventory_handler.shift_container.container_B = self.slots
