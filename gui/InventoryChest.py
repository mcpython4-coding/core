"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import gui.Inventory
import gui.Slot
import gui.ItemStack
import crafting.CraftingHandler
import crafting.GridRecipeInterface
import gui.ItemStack


class InventoryChest(gui.Inventory.Inventory):
    """
    inventory class for chest
    """

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/blockinventorychest.json"

    def on_create(self):
        pass

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
        for slot in G.player.inventorys["main"].slots[:36] + self.slots:
            slot.draw(x, y, hovering=slot == hoveringslot)
        self.on_draw_over_image()
        for slot in self.slots:
            slot.draw_lable()
        self.on_draw_overlay()

    def get_interaction_slots(self):
        return G.player.inventorys["main"].slots[:36] + self.slots

