"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from pyglet.window import mouse, key
import gui.InventoryCraftingTable
import item.ItemTool


@G.registry
class BlockCraftingTable(Block.Block):
    inventory = None

    @staticmethod
    def get_name() -> str:
        return "minecraft:crafting_table"

    def on_player_interact(self, itemstack, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        """
        called to get an list of inventories
        """
        return [self.inventory]

    def get_hardness(self):
        return 2.5

    def get_minimum_tool_level(self):
        return 0

    def get_best_tools(self):
        return [item.ItemTool.ToolType.AXE]

