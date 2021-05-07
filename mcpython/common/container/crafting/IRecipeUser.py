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
import typing

import mcpython.common.container.crafting.IRecipe
import mcpython.common.event.Registry
from mcpython.common.container.ResourceStack import ItemStack


class IRecipeUser(mcpython.common.event.Registry.IRegistryContent):
    """
    Abstract marker for a thing supporting recipes.
    Any recipe may be linked. There may be none recipe linked.
    Not every recipe type may link a IRecipeUser
    Recipe users capable of linking to a current inventory or similar should implement
    insert_items() and override CAN_INSERT_ITEMS to True
    """

    TYPE = "minecraft:recipe_user"
    CAN_INSERT_ITEMS = False

    RECIPE_TYPES: typing.List[str] = []

    @classmethod
    def on_recipe_resolved(
        cls, recipe: mcpython.common.container.crafting.IRecipe.IRecipe
    ):
        pass

    def insert_items_from(
        self,
        recipe: mcpython.common.container.crafting.IRecipe.IRecipe,
        item_source: typing.List[ItemStack],
    ) -> bool:
        return False
