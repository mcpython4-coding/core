"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.gui.InventoryChest
import mcpython.item.IShulkerBoxLikeItem
import pyglet
import mcpython.event.EventHandler
import globals as G


class InventoryShulkerBox(mcpython.gui.InventoryChest.InventoryChest):
    def create_slots(self) -> list:
        slots = super().create_slots()
        for slot in slots:
            slot.allowed_item_func = self.test_for_shulker
        return slots

    def test_for_shulker(self, itemstack):
        if itemstack.item and issubclass(type(itemstack.item), mcpython.item.IShulkerBoxLikeItem.IShulkerBoxLikeItem):
            return not itemstack.item.is_blocked_in(self)
        return True

    def on_activate(self):
        super().on_activate()
        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("user:keyboard:press", self.on_key_press)

    def on_deactivate(self):
        super().on_deactivate()
        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("user:keyboard:press", self.on_key_press)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E: G.inventoryhandler.hide(self)

    def update_shift_container(self):
        G.inventoryhandler.shift_container.container_A = G.world.get_active_player().inventories["main"].slots[:36]
        G.inventoryhandler.shift_container.container_B = self.slots

