"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import ParseBridge, ParseType, SubCommand
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
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "recipeview"
        parsebridge.add_subcommand(SubCommand(ParseType.STRING_WITHOUT_QUOTES))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        name = values[0]
        
        if name not in shared.crafting_handler.recipe_table:
            info.chat.print_ln("[ERROR] recipe '{}' is not found!".format(name))
            return

        recipe = shared.crafting_handler.recipe_table[name]
        if recipe.RECIPE_VIEW_PROVIDER is None:
            info.chat.print_ln("[ERROR] recipe '{}' of type '{}' has no view assigned!".format(
                name, type(recipe)))
            return

        shared.inventory_handler.show(cls.INVENTORY.set_renderer(recipe.RECIPE_VIEW_PROVIDER.prepare_for_recipe(recipe)))

    @staticmethod
    def get_help() -> list:
        return ["/recipeview <name>: shows the recipe as a GUI if possible"]
