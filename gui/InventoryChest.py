"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import gui.Inventory
import gui.Slot
import gui.ItemStack
import crafting.CraftingHandler
import crafting.GridRecipeInterface
import gui.ItemStack
import pyglet
import event.EventHandler


class InventoryChest(gui.Inventory.Inventory):
    """
    inventory class for chest
    """

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/blockinventorychest.json"

    def on_activate(self):
        super().on_activate()
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("user:keyboard:press", self.on_key_press)

    def on_deactivate(self):
        super().on_deactivate()
        event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("user:keyboard:press", self.on_key_press)

    def create_slots(self) -> list:
        # 3 rows of 9 slots of storage
        return [gui.Slot.Slot() for _ in range(9*3)]

    def draw(self, hoveringslot=None):
        self.on_draw_background()
        x, y = self._get_position()
        if self.bgsprite:
            self.bgsprite.position = (x, y)
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()
        for slot in G.world.get_active_player().inventories["main"].slots[:36] + self.slots:
            slot.draw(x, y, hovering=slot == hoveringslot)
        self.on_draw_over_image()
        for slot in G.world.get_active_player().inventories["main"].slots[:36] + self.slots:
            slot.draw_lable(x, y)
        self.on_draw_overlay()

    def get_interaction_slots(self):
        return G.world.get_active_player().inventories["main"].slots[:36] + self.slots

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E: G.inventoryhandler.hide(self)

    def update_shift_container(self):
        G.inventoryhandler.shift_container.container_A = G.world.get_active_player().inventories["main"].slots[:36]
        G.inventoryhandler.shift_container.container_B = self.slots

