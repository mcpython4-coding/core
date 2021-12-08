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
import mcpython.common.item.AbstractToolItem
import mcpython.util.enums
from mcpython import shared
from pyglet.window import key, mouse

from . import AbstractBlock


class CraftingTable(AbstractBlock.AbstractBlock):
    """
    Class for the crafting table
    """

    NAME: str = "minecraft:crafting_table"
    HARDNESS = BLAST_RESISTANCE = 2.5
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.AXE}

    async def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple, itemstack
    ):
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            await shared.inventory_handler.show(
                shared.world.get_active_player().inventory_crafting_table
            )
            return True
        else:
            return False

    def get_inventories(self):
        # todo: this seems not good..., maybe return None, and add a option for a internal inventory?
        return [shared.world.get_active_player().inventory_crafting_table]

    async def on_block_remove(self, reason):
        await shared.inventory_handler.hide(
            shared.world.get_active_player().inventory_crafting_table
        )

    @classmethod
    def modify_block_item(cls, factory):
        factory.set_fuel_level(15)
