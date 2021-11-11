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
import json
import random
import sys

import typing

import mcpython.client.gui.InventoryRecipeView
import mcpython.common.container.crafting.IRecipe
import mcpython.common.item.ItemManager
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
from mcpython import shared
from mcpython.common.container.crafting import IRecipe
from mcpython.engine import logger


class CraftingManager:
    RECIPE_VIEW_INVENTORY = None

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

        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "minecraft:data:shuffle:all", self.shuffle_data
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
        [self.recipe_info_table.setdefault(name, obj) for name in obj.RECIPE_TYPE_NAMES]
        return obj

    def add_recipe(
        self,
        recipe: mcpython.common.container.crafting.IRecipe.IRecipe,
        name: str = None,
    ):
        if name is None:
            name = recipe.name
        else:
            recipe.name = name

        try:
            recipe.bake()
            recipe.prepare()
        except:
            logger.print_exception("during preparing recipe " + name)
            return self

        self.recipe_table[name] = recipe
        return self

    def add_recipe_from_data(self, data: dict, name: str, file: str = None):
        recipe_type = data["type"]
        if recipe_type in self.recipe_info_table:
            try:
                recipe = self.recipe_info_table[recipe_type].from_data(data, file)
            except:
                logger.print_exception(f"during decoding {file}")
                recipe = None

            if recipe is None:
                return 0
            self.add_recipe(recipe, name)
            return recipe
        else:
            logger.println(
                f"[RECIPE MANAGER][WARN] failed to find recipe decoder '{recipe_type}' for recipe '{name}'"
            )
            return None

    def add_recipe_from_file(self, file: str):
        try:
            data = mcpython.engine.ResourceLoader.read_raw(file).decode("utf-8")
        except:
            logger.print_exception("during loading recipe file '{}'".format(file))
            return

        if len(data.strip()) == 0:
            return

        try:
            data = json.loads(data)
        except:
            logger.print_exception(
                "during json-decoding recipe from file '{}'".format(file),
                "'" + data + "'",
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
        for file in mcpython.engine.ResourceLoader.get_all_entries(
            "data/{}/recipes".format(modname)
        ):
            if file.endswith("/"):
                continue

            if not load_direct:
                shared.mod_loader.mods[modname].eventbus.subscribe(
                    "stage:recipe:on_bake",
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
        # all shaped recipes sorted after item count and then size
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

    def show_to_player(self, recipe_name: str | IRecipe.IRecipe):
        # todo: show error messages in chat

        if isinstance(recipe_name, str):
            if recipe_name not in self.recipe_table:
                logger.println(f"recipe '{recipe_name}' was not found!")
                return

            recipe = self.recipe_table[recipe_name]
        else:
            recipe = recipe_name

        if recipe.RECIPE_VIEW is None:
            logger.println(f"recipe {recipe_name} does not support showing")
            return

        if self.RECIPE_VIEW_INVENTORY is None or not isinstance(self.RECIPE_VIEW_INVENTORY, mcpython.client.gui.InventoryRecipeView.InventorySingleRecipeView):
            self.RECIPE_VIEW_INVENTORY = (
                mcpython.client.gui.InventoryRecipeView.InventorySingleRecipeView()
            )

        shared.inventory_handler.show(
            self.RECIPE_VIEW_INVENTORY.set_renderer(
                recipe.RECIPE_VIEW.prepare_for_recipe(recipe)
            )
        )

    def show_to_player_from_input(self, input_name: str):
        recipes = []

        for array in self.crafting_recipes_shapeless.values():
            for recipe in array:
                if any(any(x[0] == input_name for x in e) for e in recipe.inputs):
                    recipes.append(recipe)

        for array1 in self.crafting_recipes_shaped.values():
            for array2 in array1.values():
                for recipe in array2:
                    if any(any(x[0] == input_name for x in e) for e in recipe.inputs.values()):
                        recipes.append(recipe)

        if not recipes:
            logger.println(f"[WARN] no recipes found using item {input_name}")
            return

        self.show_recipe_list(recipes)

    def show_to_player_from_output(self, output_name: str):
        recipes = []

        for array in self.crafting_recipes_shapeless.values():
            for recipe in array:
                if recipe.output[0] == output_name:
                    recipes.append(recipe)

        for array1 in self.crafting_recipes_shaped.values():
            for array2 in array1.values():
                for recipe in array2:
                    if recipe.output[0] == output_name:
                        recipes.append(recipe)

        if not recipes:
            logger.println(f"[WARN] no recipes found outputting {output_name}")
            return

        self.show_recipe_list(recipes)

    def show_recipe_list(self, recipes: typing.List[IRecipe.IRecipe]):
        self.RECIPE_VIEW_INVENTORY = (
            mcpython.client.gui.InventoryRecipeView.InventoryMultiRecipeView()
        )

        for recipe in recipes[:]:
            while recipes.count(recipe) > 1:
                recipes.remove(recipe)

        for recipe in recipes:
            self.RECIPE_VIEW_INVENTORY.add_recipe_renderer(recipe.RECIPE_VIEW.copy().prepare_for_recipe(recipe))

            if recipe.RECIPE_VIEW is None:
                logger.println(f"recipe {recipe.name} does not support showing")
                self.RECIPE_VIEW_INVENTORY = None
                return

        shared.inventory_handler.show(
            self.RECIPE_VIEW_INVENTORY
        )


shared.crafting_handler = CraftingManager()


def load_recipe_providers():
    from . import (
        FurnaceCraftingHelper,
        GridRecipeInstances,
        SmithingRecipe,
        StonecuttingRecipe,
    )


if not shared.IS_TEST_ENV:
    import mcpython.common.mod.ModMcpython

    mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
        "stage:recipe:groups",
        load_recipe_providers,
        info="loading crafting recipe groups",
    )
