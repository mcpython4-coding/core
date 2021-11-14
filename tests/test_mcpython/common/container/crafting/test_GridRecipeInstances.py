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
from unittest import TestCase

from mcpython.common.container.ResourceStack import ItemStack


class TestAbstractCraftingGridRecipe(TestCase):
    def test_module_import(self):
        import mcpython.common.container.crafting.GridRecipeInstances


class TestGridShaped(TestCase):
    def setUp(self):
        from mcpython.common.container.crafting.GridRecipeInstances import GridShaped
        from mcpython.common.factory.ItemFactory import ItemFactory

        ItemFactory().set_name("minecraft:oak_planks").finish()
        ItemFactory().set_name("minecraft:oak_slab").finish()

        data = {
            "type": "minecraft:crafting_shaped",
            "group": "wooden_slab",
            "pattern": ["###"],
            "key": {"#": {"item": "minecraft:oak_planks"}},
            "result": {"item": "minecraft:oak_slab", "count": 6},
        }
        self.example_recipe = GridShaped.from_data(data, "test::file")

    def test_from_data(self):
        self.assertIsNotNone(self.example_recipe)
        self.assertEqual(self.example_recipe.bounding_box_size, (3, 1))
        self.assertEqual(
            {key: value[0][0] for key, value in self.example_recipe.inputs.items()},
            {
                (0, 0): "minecraft:oak_planks",
                (1, 0): "minecraft:oak_planks",
                (2, 0): "minecraft:oak_planks",
            },
        )
        self.assertEqual(self.example_recipe.output, ("minecraft:oak_slab", 6))

    def test_as_grid(self):
        grid = self.example_recipe.as_grid()
        self.assertEqual(
            grid,
            [
                [[("minecraft:oak_planks", 1)], None, None],
                [[("minecraft:oak_planks", 1)], None, None],
                [[("minecraft:oak_planks", 1)], None, None],
            ],
        )

    def tearDown(self):
        self.example_recipe = None


class TestGridShapeless(TestCase):
    def setUp(self):
        from mcpython.common.container.crafting.GridRecipeInstances import GridShapeless
        from mcpython.common.factory.ItemFactory import ItemFactory

        ItemFactory().set_name("minecraft:oak_planks").finish()
        ItemFactory().set_name("minecraft:oak_button").finish()

        data = {
            "type": "minecraft:crafting_shapeless",
            "group": "wooden_button",
            "ingredients": [{"item": "minecraft:oak_planks"}],
            "result": {"item": "minecraft:oak_button"},
        }

        self.example_recipe = GridShapeless.from_data(data, "test::file")

    def test_from_data(self):
        self.assertEqual(self.example_recipe.inputs, [[("minecraft:oak_planks", 1)]])
        self.assertEqual(self.example_recipe.output, ("minecraft:oak_button", 1))

    def test_as_grid_for_view(self):
        grid = self.example_recipe.as_grid_for_view()

        self.assertEqual(
            grid,
            (
                [
                    [[ItemStack("minecraft:oak_planks", 1)], None, None],
                    [None, None, None],
                    [None, None, None],
                ],
                ItemStack("minecraft:oak_button", 1),
            ),
        )
