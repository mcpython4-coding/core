"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import mcpython.gui.crafting.IRecipeType
import mcpython.ResourceLocator
import mcpython.item.ItemHandler
import mcpython.mod.ModMcpython
import mcpython.event.EventHandler
import sys
import logger
import random
import json


class CraftingHandler:
    def __init__(self):
        # todo: add special registry for recipes
        self.recipeinfotable = {}

        self.recipe_table = {}

        self.recipe_relink_table = {}

        # all shapeless recipes sorted after item count
        self.crafting_recipes_shapeless = {}
        # all shaped recipes sorted after item count and than size
        self.crafting_recipes_shaped = {}
        # all smelting outputs sorted after ingredient
        self.furnace_recipes = {}

        self.loaded_mod_dirs = set()

        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("data:shuffle:all", self.shuffle_data)

    def shuffle_data(self):
        recipe_groups = {}
        for recipe in self.recipe_table.values():
            recipe_groups.setdefault(recipe.__class__.__name__, []).append(recipe)
        recipe_group_copy = {key: recipe_groups[key].copy() for key in recipe_groups}
        for group in recipe_groups:
            for recipe in recipe_groups[group]:
                recipe_2 = random.choice(recipe_group_copy[group])
                self.recipe_relink_table[recipe.name] = recipe_2.name
                recipe_group_copy[group].remove(recipe_2)

    def check_relink(self, recipe):
        name = recipe.name
        if name in self.recipe_relink_table:
            return self.recipe_table[self.recipe_relink_table[name]]
        return recipe

    def __call__(self, obj):
        if issubclass(obj, mcpython.gui.crafting.IRecipeType.IRecipe):
            [self.recipeinfotable.setdefault(name, obj) for name in obj.get_recipe_names()]
        else:
            raise ValueError()
        return obj

    def add_recipe(self, recipe: mcpython.gui.crafting.IRecipeType.IRecipe, name):
        recipe.name = name
        recipe.register()
        self.recipe_table[name] = recipe

    def add_recipe_from_data(self, data: dict, name: str):
        rname = data["type"]
        if rname in self.recipeinfotable:
            recipe = self.recipeinfotable[rname].from_data(data)
            if recipe is None:
                return 0
            self.add_recipe(recipe, name)
            return recipe
        else:
            return None

    def add_recipe_from_file(self, file: str):
        try:
            data = mcpython.ResourceLocator.read(file).decode("utf-8")
        except:
            logger.write_exception("during loading recipe file '{}'".format(file))
            return
        if len(data.strip()) == 0: return
        try:
            data = json.loads(data)
        except:
            logger.write_exception("during decoding recipe from file '{}'".format(file), "'"+data+"'")
            return
        s = file.split("/")
        name = "{}:{}".format(s[s.index("data")+1], "/".join(s[s.index("recipes")+1:]))
        result = self.add_recipe_from_data(data, name)
        if result is None and "--debugrecipes" in sys.argv:
            logger.println("error in decoding recipe from file {}: type '{}' not found".format(file, data["type"]))

    def load(self, modname, check_mod_dirs=True, load_direct=False):
        if modname in self.loaded_mod_dirs and check_mod_dirs:
            logger.println("ERROR: mod '{}' has tried to load crafting recipes twice or more".format(modname))
            return  # make sure to load only ones!
        self.loaded_mod_dirs.add(modname)
        for itemname in mcpython.ResourceLocator.get_all_entries("data/{}/recipes".format(modname)):
            if itemname.endswith("/"): continue
            if not load_direct:
                G.modloader.mods[modname].eventbus.subscribe("stage:recipe:bake", self.add_recipe_from_file, itemname,
                                                             info="loading crafting recipe from {}".format(itemname))
            else:
                self.add_recipe_from_file(itemname)

    def reload_crafting_recipes(self):
        if not G.eventhandler.call_cancelable("craftinghandler:reload:pre", self): return

        # all shapeless recipes sorted after item count
        self.crafting_recipes_shapeless = {}
        # all shaped recipes sorted after item count and than size
        self.crafting_recipes_shaped = {}
        # all smelting outputs sorted after ingredient
        self.furnace_recipes = {}

        G.eventhandler.call("craftinghandler:reload:intermediate", self)

        for i, modname in enumerate(list(self.loaded_mod_dirs)):
            logger.println("\r[MODLOADER][INFO] reloading mod recipes for mod {} ({}/{})".format(
                modname, i+1, len(self.loaded_mod_dirs)), end="")
            self.load(modname, check_mod_dirs=False, load_direct=True)
        logger.println()

        G.eventhandler.call("craftinghandler:reload:end", self)


G.craftinghandler = CraftingHandler()


def load_recipe_providers():
    pass


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:recipe:groups", load_recipe_providers,
                                            info="loading crafting recipe groups")
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:recipes", G.craftinghandler.load, "minecraft",
                                            info="loading crafting recipes")

