"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals as G
from . import Block
from pyglet.window import mouse, key
import mcpython.util.enums
import mcpython.common.factory.ItemFactory
import mcpython.common.item.IShulkerBoxLikeItem


def create_shulker_box(name):
    @G.registry
    class BlockShulkerBox(Block.Block):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            import mcpython.client.gui.InventoryShulkerBox as InventoryShulkerBox

            self.inventory = InventoryShulkerBox.InventoryShulkerBox()

        NAME = "minecraft:{}".format(name)

        def on_player_interaction(
            self, player, button: int, modifiers: int, hit_position: tuple
        ):
            if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
                G.inventoryhandler.show(self.inventory)
                return True
            else:
                return False

        def get_inventories(self):
            return [self.inventory]

        HARDNESS = 2.5
        MINIMUM_TOOL_LEVEL = 0
        BEST_TOOLS_TO_BREAK = [mcpython.util.enums.ToolType.AXE]

        def get_provided_slot_lists(self, side):
            return self.inventory.slots, self.inventory.slots

        @classmethod
        def modify_block_item(
            cls, itemconstructor: mcpython.common.factory.ItemFactory.ItemFactory
        ):
            itemconstructor.setMaxStackSize(1)
            itemconstructor.baseclass.append(
                mcpython.common.item.IShulkerBoxLikeItem.IShulkerBoxLikeItem
            )
            itemconstructor.setCustomFromItemFunction(cls.set_block_data)

        @classmethod
        def set_block_data(cls, iteminst, block):
            if hasattr(iteminst, "inventory"):
                block.inventory = iteminst.inventory.copy()

        def on_request_item_for_block(self, itemstack):
            itemstack.item.inventory = self.inventory.copy()

        def on_remove(self):
            G.inventoryhandler.hide(self.inventory)


@G.modloader("minecraft", "stage:block:load")
def load():
    create_shulker_box("shulker_box")
    for color in mcpython.util.enums.COLORS:
        create_shulker_box("{}_shulker_box".format(color))
