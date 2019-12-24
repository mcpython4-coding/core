"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import crafting.IRecipeType
import json
import ResourceLocator
import item.ItemHandler
import traceback
import mod.ModMcpython
import sys


class CraftingHandler:
    def __init__(self):
        self.recipeinfotable = {}

        # all shapeless recipes sorted after item count
        self.crafting_recipes_shapeless = {}
        # all shaped recipes sorted after item count and than size
        self.crafting_recipes_shaped = {}
        self.loaded_mod_dirs = []

    def __call__(self, obj):
        if issubclass(obj, crafting.IRecipeType.IRecipe):
            [self.recipeinfotable.setdefault(name, obj) for name in obj.get_recipe_names()]
        else:
            raise ValueError()
        return obj

    def add_recipe(self, recipe: crafting.IRecipeType.IRecipe):
        recipe.register()

    def add_recipe_from_data(self, data: dict):
        name = data["type"]
        if name in self.recipeinfotable:
            recipe = self.recipeinfotable[name].from_data(data)
            if recipe is None:
                return 0
            self.add_recipe(recipe)
            return recipe
        else:
            return None

    def add_recipe_from_file(self, file: str):
        data = ResourceLocator.read(file, "json")
        result = self.add_recipe_from_data(data)
        if result is None and "--debugrecipes" in sys.argv:
            print("error in decoding recipe from file {}: type '{}' not found".format(file, data["type"]))

    def load(self, modname):
        if modname in self.loaded_mod_dirs:
            print("ERROR: mod '{}' has tried to load crafting recipes twice or more".format(modname))
            return  # make sure to load only ones!
        self.loaded_mod_dirs.append(modname)
        for itemname in ResourceLocator.get_all_entries("data/{}/recipes".format(modname)):
            G.modloader.mods[modname].eventbus.subscribe("stage:recipe:bake", self.add_recipe_from_file, itemname,
                                                         info="loading crafting recipe from {}".format(itemname))


G.craftinghandler = CraftingHandler()


def load_recipe_providers():
    from . import (GridRecipes)


mod.ModMcpython.mcpython.eventbus.subscribe("stage:recipe:groups", load_recipe_providers,
                                            info="loading crafting recipe groups")
mod.ModMcpython.mcpython.eventbus.subscribe("stage:recipes", G.craftinghandler.load, "minecraft",
                                            info="loading crafting recipes")

