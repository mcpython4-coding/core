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
import mcpython.common.item.AbstractToolItem


class BlockCraftingTable(AbstractBlock.AbstractBlock):
    """
    Class for the crafting table
    """

    NAME: str = "minecraft:crafting_table"
    HARDNESS = 2.5
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.AXE]

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            shared.inventory_handler.show(
                shared.world.get_active_player().inventory_crafting_table
            )
            return True
        else:
            return False

    def get_inventories(self):
        return [shared.world.get_active_player().inventory_crafting_table]

    def on_block_remove(self, reason):
        shared.inventory_handler.hide(
            shared.world.get_active_player().inventory_crafting_table
        )

    @classmethod
    def modify_block_item(cls, factory):
        factory.set_fuel_level(15)


@shared.mod_loader("minecraft", "stage:block:load")
def load():
    shared.registry.register(BlockCraftingTable)
