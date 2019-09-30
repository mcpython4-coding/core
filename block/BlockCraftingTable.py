"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from pyglet.window import mouse, key
import gui.InventoryCraftingTable


@G.registry
class BlockCraftingTable(Block.Block):
    inventory = gui.InventoryCraftingTable.InventoryCraftingTable()

    @staticmethod
    def get_name() -> str:
        return "minecraft:crafting_table"

    def on_player_interact(self, itemstack, button, modifiers) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

