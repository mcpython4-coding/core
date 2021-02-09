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
from mcpython import logger
from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    Node,
)
import mcpython.util.math
import mcpython.client.gui.InventoryRecipeView


@shared.registry
class CommandRecipeView(mcpython.server.command.Command.Command):
    """
    Class for the /recipeview command
    """

    NAME = "minecraft:recipe_view"
    INVENTORY = mcpython.client.gui.InventoryRecipeView.InventorySingleRecipeView()

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "recipeview"
        command_syntax_holder.add_node(Node(CommandArgumentType.STRING_WITHOUT_QUOTES))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        name = values[0]

        if name not in shared.crafting_handler.recipe_table:
            info.chat.print_ln(
                "[RECIPE VIEW][ERROR] recipe '{}' is not found!".format(name)
            )
            return

        recipe = shared.crafting_handler.recipe_table[name]
        if recipe.RECIPE_VIEW is None:
            info.chat.print_ln(
                "[RECIPE VIEW][ERROR] recipe '{}' of type '{}' has no view assigned!".format(
                    name, type(recipe)
                )
            )
            return

        shared.inventory_handler.show(
            cls.INVENTORY.set_renderer(recipe.RECIPE_VIEW.prepare_for_recipe(recipe))
        )

    @staticmethod
    def get_help() -> list:
        return ["/recipeview <name>: shows the recipe as a GUI if possible"]
