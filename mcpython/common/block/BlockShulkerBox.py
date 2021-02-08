"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from . import AbstractBlock
from pyglet.window import mouse, key
import mcpython.util.enums
import mcpython.common.factory.ItemFactory


def create_shulker_box(name):
    @shared.registry
    class BlockShulkerBox(AbstractBlock.AbstractBlock):
        def __init__(self):
            super().__init__()
            import mcpython.client.gui.InventoryShulkerBox as InventoryShulkerBox

            self.inventory = InventoryShulkerBox.InventoryShulkerBox()

        NAME = "minecraft:{}".format(name)

        DEFAULT_FACE_SOLID = (
            mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
        )

        def on_player_interaction(
            self, player, button: int, modifiers: int, hit_position: tuple
        ):
            if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
                shared.inventory_handler.show(self.inventory)
                return True
            else:
                return False

        def get_inventories(self):
            return (self.inventory,)

        HARDNESS = 2.5
        MINIMUM_TOOL_LEVEL = 0
        ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.AXE]

        def get_provided_slot_lists(self, side):
            return self.inventory.slots, self.inventory.slots

        @classmethod
        def modify_block_item(
            cls, item_constructor: mcpython.common.factory.ItemFactory.ItemFactory
        ):
            item_constructor.set_max_stack_size(1)
            item_constructor.set_custom_from_item_function(cls.set_block_data)

        @classmethod
        def set_block_data(cls, item_instance, block):
            if hasattr(item_instance, "inventory"):
                block.inventory = item_instance.inventory.copy()

        def on_request_item_for_block(self, itemstack):
            itemstack.item.inventory = self.inventory.copy()

        def on_block_remove(self, reason):
            shared.inventory_handler.hide(self.inventory)


@shared.mod_loader("minecraft", "stage:block:load")
def load():
    create_shulker_box("shulker_box")
    for color in mcpython.util.enums.COLORS:
        create_shulker_box("{}_shulker_box".format(color))
