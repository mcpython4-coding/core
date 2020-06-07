"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.gui.Inventory
import mcpython.gui.Slot
import mcpython.gui.ItemStack
import mcpython.crafting.CraftingHandler
import mcpython.crafting.GridRecipeInterface
import pyglet
import mcpython.event.EventHandler


class InventoryCraftingTable(mcpython.gui.Inventory.Inventory):
    """
    inventory class for the crafting table
    """

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/blockinventorycraftingtable.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inputs = [self.slots[:3], self.slots[3:6], self.slots[6:9]]
        self.recipeinterface = mcpython.crafting.GridRecipeInterface.GridRecipeInterface(inputs, self.slots[9])

    def create_slots(self) -> list:
        # 36 slots of main, 9 crafting grid, 1 crafting output
        # base_slots = G.world.get_active_player().inventories["main"].slots[:36]
        return [mcpython.gui.Slot.Slot() for _ in range(10)]

    def on_activate(self):
        super().on_activate()
        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("user:keyboard:press", self.on_key_press)

    def on_deactivate(self):
        super().on_deactivate()
        for slot in self.slots[:-1]:
            G.world.get_active_player().pick_up(slot.get_itemstack().copy())
            slot.get_itemstack().clean()
        self.slots[-1].itemstack.clean()
        self.slots[-1].get_itemstack().clean()
        G.world.get_active_player().reset_moving_slot()
        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("user:keyboard:press", self.on_key_press)

    def draw(self, hoveringslot=None):
        """
        draws the inventory
        """
        self.on_draw_background()
        x, y = self.get_position()
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

