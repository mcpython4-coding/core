"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.factory.ItemFactory
import mcpython.util.enums
from mcpython import shared
from mcpython.client.rendering.blocks.ShulkerBoxRenderer import ShulkerBoxRenderer
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from pyglet.window import key, mouse

from . import AbstractBlock


def create_shulker_box(name):
    @shared.registry
    class ShulkerBox(AbstractBlock.AbstractBlock):
        NAME = "minecraft:{}".format(name)

        DEFAULT_FACE_SOLID = (
            mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
        )

        HARDNESS = 2.5
        MINIMUM_TOOL_LEVEL = 0
        ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.AXE}

        if shared.IS_CLIENT:
            RENDERER = ShulkerBoxRenderer("minecraft:block/" + name)

            def on_block_added(self):
                self.face_info.custom_renderer = self.RENDERER

        def __init__(self):
            super().__init__()
            import mcpython.client.gui.InventoryShulkerBox as InventoryShulkerBox

            self.inventory = InventoryShulkerBox.InventoryShulkerBox()

        def write_to_network_buffer(self, buffer: WriteBuffer):
            super().write_to_network_buffer(buffer)
            self.inventory.write_to_network_buffer(buffer)

        def read_from_network_buffer(self, buffer: ReadBuffer):
            super().read_from_network_buffer(buffer)
            self.inventory.read_from_network_buffer(buffer)

        def on_player_interaction(
            self,
            player,
            button: int,
            modifiers: int,
            hit_position: tuple,
            itemstack,
        ):
            if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
                shared.inventory_handler.show(self.inventory)
                return True
            else:
                return False

        def get_inventories(self):
            return (self.inventory,)

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


def load():
    create_shulker_box("shulker_box")
    for color in mcpython.util.enums.COLORS:
        create_shulker_box("{}_shulker_box".format(color))
