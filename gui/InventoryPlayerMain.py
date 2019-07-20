"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import gui.Inventory
import gui.Slot


class InventoryPlayerMain(gui.Inventory.Inventory):
    @staticmethod
    def get_config_file() -> str or None:
        return G.local+"/assets/config/inventory/playerinventorymain.json"

    def on_create(self):
        pass

    def create_slots(self) -> list:
        # 9x hotbar, 27x main, 4x armor, 5x crafting, 1x offhand
        return [G.player.inventorys["hotbar"].slots[i].copy() for i in range(9)] + [gui.Slot.Slot() for _ in range(37)]

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_draw_background(self):
        pass

    def on_draw_over_backgroundimage(self):
        pass

    def on_draw_over_image(self):
        pass

    def on_draw_overlay(self):
        pass

