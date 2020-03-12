"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Block
from pyglet.window import mouse, key
import gui.InventoryCraftingTable
import item.ItemTool


@G.registry
class BlockCraftingTable(Block.Block):
    NAME = "minecraft:crafting_table"

    def on_player_interact(self, player, itemstack, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventoryhandler.show(G.world.get_active_player().inventories["crafting_table"])
            return True
        else:
            return False

    def get_inventories(self):
        """
        called to get an list of inventories
        """
        return [G.world.get_active_player().inventories["crafting_table"]]

    def get_hardness(self):
        return 2.5

    def get_best_tools(self):
        return [item.ItemTool.ToolType.AXE]

    def on_remove(self):
        G.inventoryhandler.hide(G.world.get_active_player().inventories["crafting_table"])

    @classmethod
    def modify_block_item(cls, itemfactory):
        itemfactory.setFuelLevel(15)

