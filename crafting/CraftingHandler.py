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


class CraftingHandler:
    def __init__(self):
        self.recipeinfotable = {}

        # used for both shaped and shapeless recipes
        # an used_items: int -> recipes: IRecipe[
        self.crafting_recipes = {}

    def __call__(self, obj):
        if issubclass(obj, crafting.IRecipeType.IRecipe):
            self.recipeinfotable[obj.get_recipe_name()] = obj
        else:
            raise ValueError()
        return obj

    def add_recipe(self, recipe: crafting.IRecipeType.IRecipe):
        recipe.register()

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
        excepted = 0
        for item in ResourceLocator.get_all_entrys("data/minecraft/recipes"):
            print("\r -loading recipe {}".format(i), end="")
            try:
                self.add_recipe_from_file(item)
            except ValueError:
                errored += 1
            except:
                print("\rerror during loading recipe", item)
                traceback.print_exc()
                excepted += 1
            i += 1
        print("\nnot loadable recipes due to missing decoders: {}".format(errored) if errored else "")
        if excepted: print("not loadable recipes due to loading exceptions: {}".format(excepted))


G.craftinghandler = CraftingHandler()

from . import (GridRecipes)

