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
from mcpython import shared, logger
import mcpython.common.container.crafting.IRecipe
import mcpython.ResourceLoader
import mcpython.common.item.ItemHandler
import mcpython.common.mod.ModMcpython
import mcpython.common.event.EventHandler
import sys
import random
import json


class CraftingManager:
    def __init__(self):
        # todo: add special registry for recipes
        self.recipe_info_table = {}

        self.recipe_table = {}

        self.recipe_relink_table = {}

        # all shapeless recipes sorted after item count
        self.crafting_recipes_shapeless = {}
        # all shaped recipes sorted after item count and than size
        self.crafting_recipes_shaped = {}
        # all smelting outputs sorted after ingredient
        self.furnace_recipes = {}

        self.loaded_mod_dirs = set()

        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "data:shuffle:all", self.shuffle_data
        )

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

    def check_relink(self, recipe: mcpython.common.container.crafting.IRecipe.IRecipe):
        name = recipe.name
        if name in self.recipe_relink_table:
            return self.recipe_table[self.recipe_relink_table[name]]
        return recipe

    def __call__(self, obj):
        if issubclass(obj, mcpython.common.container.crafting.IRecipe.IRecipe):
            [
                self.recipe_info_table.setdefault(name, obj)
                for name in obj.RECIPE_TYPE_NAMES
            ]
        else:
            raise ValueError(obj)
        return obj

    def add_recipe(
        self, recipe: mcpython.common.container.crafting.IRecipe.IRecipe, name: str
    ):
        recipe.name = name
        recipe.bake()
        recipe.prepare()
        self.recipe_table[name] = recipe

    def add_recipe_from_data(self, data: dict, name: str, file: str = None):
        recipe_type = data["type"]
        if recipe_type in self.recipe_info_table:
            recipe = self.recipe_info_table[recipe_type].from_data(data, file)
            if recipe is None:
                return 0
            self.add_recipe(recipe, name)
            return recipe
        else:
            return None

    def add_recipe_from_file(self, file: str):
        try:
            data = mcpython.ResourceLoader.read_raw(file).decode("utf-8")
        except:
            logger.print_exception("during loading recipe file '{}'".format(file))
            return

        if len(data.strip()) == 0:
            return

        try:
            data = json.loads(data)
        except:
            logger.print_exception(
                "during decoding recipe from file '{}'".format(file), "'" + data + "'"
            )
            return

        s = file.split("/")
        name = "{}:{}".format(
            s[s.index("data") + 1], "/".join(s[s.index("recipes") + 1 :])
        ).removesuffix(".json")
        # todo: add option to run later
        result = self.add_recipe_from_data(data, name, file)

        if result is None and "--debugrecipes" in sys.argv:
            logger.println(
                "error in decoding recipe from file '{}': type '{}' not found".format(
                    file, data["type"]
                )
            )

    def load(self, modname: str, check_mod_dirs=True, load_direct=False):
        if modname in self.loaded_mod_dirs and check_mod_dirs:
            logger.println(
                "ERROR: mod '{}' has tried to load crafting recipes twice or more".format(
                    modname
                )
            )
            return  # make sure to load only ones!
        self.loaded_mod_dirs.add(modname)
        for file in mcpython.ResourceLoader.get_all_entries(
            "data/{}/recipes".format(modname)
        ):
            if file.endswith("/"):
                continue
            if not load_direct:
                shared.mod_loader.mods[modname].eventbus.subscribe(
                    "stage:recipe:bake",
                    self.add_recipe_from_file,
                    file,
                    info="loading crafting recipe from {}".format(file),
                )
            else:
                self.add_recipe_from_file(file)

    def reload_crafting_recipes(self):
        if not shared.event_handler.call_cancelable(
            "crafting_manager:reload:pre", self
        ):
            return

        # all shapeless recipes sorted after item count
        self.crafting_recipes_shapeless = {}
        # all shaped recipes sorted after item count and than size
        self.crafting_recipes_shaped = {}
        # all smelting outputs sorted after ingredient
        self.furnace_recipes = {}

        shared.event_handler.call("crafting_manager:reload:intermediate", self)

        for i, modname in enumerate(list(self.loaded_mod_dirs)):
            print(
                "\r[MOD LOADER][INFO] reloading mod recipes for mod {} ({}/{})".format(
                    modname, i + 1, len(self.loaded_mod_dirs)
                ),
                end="",
            )
            self.load(modname, check_mod_dirs=False, load_direct=True)
        print()

        shared.event_handler.call("crafting_manager:reload:end", self)


shared.crafting_handler = CraftingManager()


def load_recipe_providers():
    pass


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:recipe:groups", load_recipe_providers, info="loading crafting recipe groups"
)
