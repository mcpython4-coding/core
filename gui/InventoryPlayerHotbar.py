"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import gui.Inventory
import gui.InventoryHandler
import gui.Slot
import pyglet
import ResourceLocator


class InventoryPlayerHotbar(gui.Inventory.Inventory):
    """
    main inventory for the hotbar
    """

    def __init__(self):
        gui.Inventory.Inventory.__init__(self)
        self.selected_sprite = pyglet.sprite.Sprite(ResourceLocator.read("tmp/gui/selected_slot.png", "pyglet"))

    @staticmethod
    def get_config_file():
        return "assets/config/inventory/playerinventoryhotbar.json"

    def is_blocking_interactions(self) -> bool:
        return False

    def create_slots(self) -> list:
        return [gui.Slot.Slot() for _ in range(9)]

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_draw_over_image(self):
        x, y = G.player.get_active_inventory_slot().position
        dx, dy = tuple(self.config["selected_delta"]) if "selected_delta" in self.config else (8, 8)
        x -= dx
        y -= dy
        dx, dy = self._get_position()
        x += dx
        y += dy
        self.selected_sprite.position = (x, y)
        self.selected_sprite.draw()

    def is_closable_by_escape(self) -> bool: return False

    def is_always_open(self) -> bool: return True

