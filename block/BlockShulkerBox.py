"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from pyglet.window import mouse, key
import item.ItemTool
import util.enums
import factory.ItemFactory
import item.IShulkerBoxLikeItem


def create_shulker_box(name):

    @G.registry
    class BlockShulkerBox(Block.Block):
        def on_create(self):
            import gui.InventoryShulkerBox
            self.inventory = gui.InventoryShulkerBox.InventoryShulkerBox()

        @staticmethod
        def get_name() -> str:
            return "minecraft:{}".format(name)

        def on_player_interact(self, itemstack, button, modifiers, exact_hit) -> bool:
            if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
                G.inventoryhandler.show(self.inventory)
                return True
            else:
                return False

        def get_inventories(self):
            return [self.inventory]

        def get_hardness(self):
            return 2.5

        def get_minimum_tool_level(self):
            return 0

        def get_best_tools(self):
            return [item.ItemTool.ToolType.AXE]

        def get_provided_slots(self, side): return self.inventory.slots

        @classmethod
        def modify_block_item(cls, itemconstructor: factory.ItemFactory.ItemFactory):
            itemconstructor.setMaxStackSize(1)
            itemconstructor.baseclass.append(item.IShulkerBoxLikeItem.IShulkerBoxLikeItem)


create_shulker_box("shulker_box")

