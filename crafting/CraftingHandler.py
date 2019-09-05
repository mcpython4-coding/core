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


class CraftingHandler:
    def __init__(self):
        self.recipeinfotable = {}
        self.recipes = {}

    def __call__(self, obj):
        if issubclass(obj, crafting.IRecipeType.IRecipe):
            self.recipeinfotable[obj.get_recipe_name()] = obj
            self.recipes[obj.get_recipe_name()] = {}
        else:
            raise ValueError()
        return obj

    def add_recipe(self, recipe: crafting.IRecipeType.IRecipe):
        i = recipe.get_identification()
        if type(i) not in (tuple, list, set): i = [i]
        for x in i:
            if x not in self.recipes[recipe.get_recipe_name()]:  self.recipes[recipe.get_recipe_name()][x] = []
            self.recipes[recipe.get_recipe_name()][x].append(recipe)

    def add_recipe_from_data(self, data: dict):
        name = data["type"]
        if name in self.recipeinfotable:
            recipe = self.recipeinfotable[name].from_data(data)
            self.add_recipe(recipe)
            return recipe
        else:
            raise ValueError("can't load recipe. recipe class {} not arrival".format(name))

    def add_recipe_from_file(self, file: str):
        self.add_recipe_from_data(ResourceLocator.read(file, "json"))

    def load(self):
        print("loading recipes")
        i = 1
        errored = 0
        for item in ResourceLocator.get_all_entrys("data/minecraft/recipes"):
            print("\r -loading recipe {}".format(i), end="")
            try:
                self.add_recipe_from_file(item)
            except ValueError:
                errored += 1
            except:
                print(item)
                raise
            i += 1
        print("\nrecipes with errors: {}".format(errored) if errored else "")


G.craftinghandler = CraftingHandler()

from . import (GridRecipes)


# G.craftinghandler.load()

