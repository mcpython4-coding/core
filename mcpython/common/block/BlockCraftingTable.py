"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
from . import AbstractBlock
from pyglet.window import mouse, key
import mcpython.util.enums
import mcpython.common.item.ItemTool


class BlockCraftingTable(AbstractBlock.AbstractBlock):
    """
    class for the crafting table
    """

    NAME: str = "minecraft:crafting_table"

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventory_handler.show(
                G.world.get_active_player().inventory_crafting_table
            )
            return True
        else:
            return False

    def get_inventories(self):
        """
        called to get an list of inventories
        """
        return [G.world.get_active_player().inventory_crafting_table]

    HARDNESS = 2.5
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.AXE]

    def on_block_remove(self, reason):
        G.inventory_handler.hide(
            G.world.get_active_player().inventory_crafting_table
        )

    @classmethod
    def modify_block_item(cls, itemfactory):
        itemfactory.setFuelLevel(15)


@G.mod_loader("minecraft", "stage:block:load")
def load():
    G.registry.register(BlockCraftingTable)
