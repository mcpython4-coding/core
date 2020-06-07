"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Block
from pyglet.window import mouse, key
import mcpython.util.enums
import mcpython.factory.ItemFactory
import mcpython.item.IShulkerBoxLikeItem


def create_shulker_box(name):

    @G.registry
    class BlockShulkerBox(Block.Block):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            import mcpython.gui.InventoryShulkerBox as InventoryShulkerBox
            self.inventory = InventoryShulkerBox.InventoryShulkerBox()

        NAME = "minecraft:{}".format(name)

        def on_player_interact(self, player, itemstack, button, modifiers, exact_hit) -> bool:
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

        def get_provided_slots(self, side): return self.inventory.slots

        @classmethod
        def modify_block_item(cls, itemconstructor: mcpython.factory.ItemFactory.ItemFactory):
            itemconstructor.setMaxStackSize(1)
            itemconstructor.baseclass.append(mcpython.item.IShulkerBoxLikeItem.IShulkerBoxLikeItem)
            itemconstructor.setCustomFromItemFunction(cls.set_block_data)

        @classmethod
        def set_block_data(cls, iteminst, block):
            if hasattr(iteminst, "inventory"):
                block.inventory = iteminst.inventory.copy()

        def on_request_item_for_block(self, itemstack):
            itemstack.item.inventory = self.inventory.copy()

        def on_remove(self):
            G.inventoryhandler.hide(self.inventory)


create_shulker_box("shulker_box")
for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
    create_shulker_box("{}_shulker_box".format(color))
