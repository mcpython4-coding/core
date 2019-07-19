"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import gui.Inventory
import gui.InventoryHandler
import gui.Slot
import texture.helpers
import ResourceLocator


class InventoryPlayerHotbar(gui.Inventory.Inventory):
    @staticmethod
    def get_config_file():
        return G.local+"/assets/config/inventory/playerinventoryhorbar.json"

    def on_create(self):
        self.bgsprite = texture.helpers.to_pyglet_sprite(ResourceLocator.ResourceLocator("tmp/gui/hotbar.png").data)
        self.bgimagesize = (364, 44)
        self.windowanchor = "MD"
        self.positon = (0, 100)

    def is_blocking_interactions(self) -> bool:
        return False

    def create_slots(self) -> list:
        return [gui.Slot.Slot() for _ in range(9)]

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def is_closable_by_escape(self) -> bool: return False

    def is_always_open(self) -> bool: return True

