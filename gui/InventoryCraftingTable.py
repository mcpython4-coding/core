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
import pyglet
import event.EventHandler


class InventoryCraftingTable(gui.Inventory.Inventory):
    """
    inventory class for the crafting table
    """

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/blockinventorycraftingtable.json"

    def on_create(self):
        inputs = [self.slots[:3], self.slots[3:6], self.slots[6:9]]
        self.recipeinterface = crafting.GridRecipeInterface.GridRecipeInterface(inputs, self.slots[9])

    def create_slots(self) -> list:
        # 36 slots of main, 9 crafting grid, 1 crafting output
        # base_slots = G.player.inventorys["main"].slots[:36]
        return [gui.Slot.Slot() for _ in range(10)]

    def on_activate(self):
        super().on_activate()
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("user:keyboard:press", self.on_key_press)

    def on_deactivate(self):
        super().on_deactivate()
        self.slots[-1].get_itemstack().clean()
        for slot in self.slots[:-1]:
            G.player.add_to_free_place(slot.get_itemstack())
            slot.get_itemstack().clean()
        G.player.reset_moving_slot()
        event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("user:keyboard:press", self.on_key_press)

    def draw(self, hoveringslot=None):
        """
        draws the inventory
        """
        self.on_draw_background()
        x, y = self._get_position()
        if self.bgsprite:
            self.bgsprite.position = (x, y)
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()
        for slot in G.player.inventorys["main"].slots[:36] + self.slots:
            slot.draw(x, y, hovering=slot == hoveringslot)
        self.on_draw_over_image()
        for slot in G.player.inventorys["main"].slots[:36] + self.slots:
            slot.draw_lable(x, y)
        self.on_draw_overlay()

    def get_interaction_slots(self):
        return G.player.inventorys["main"].slots[:36] + self.slots

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E: G.inventoryhandler.hide(self)

