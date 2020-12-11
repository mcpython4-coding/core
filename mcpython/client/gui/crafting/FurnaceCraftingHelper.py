"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.client.gui.crafting.IRecipeType
from mcpython import shared as G
import mcpython.client.gui.crafting.GridRecipeInstances


@G.crafting_handler
class FurnaceRecipe(mcpython.client.gui.crafting.IRecipeType.IRecipe):
    """
    Interface for decoding an furnace-like recipe
    """

    # The list of type descriptors to decode
    RECIPE_NAMES = ["minecraft:smelting", "minecraft:blasting", "minecraft:smoking"]

    @classmethod
    def get_recipe_names(cls) -> list:
        return cls.RECIPE_NAMES

    @classmethod
    def from_data(cls, data: dict) -> "FurnaceRecipe":
        """
        Loader function for an furnace crafting recipe
        :param data: the data to load
        :return: the recipe instance created
        """
        inputs = [
            x[0]
            for x in mcpython.client.gui.crafting.GridRecipeInstances.transform_to_item_stack(
                data["ingredient"], {}
            )
        ]
        result = data["result"]
        return cls(
            data["type"], inputs, result, data["experience"], data["cookingtime"] / 20
        )

    def __init__(self, t, i, o, xp, time):
        super().__init__()
        self.input = i
        self.output = o
        self.xp = xp
        self.time = time
        self.type = t

    def register(self):
        [
            G.crafting_handler.furnace_recipes.setdefault(self.type, {}).setdefault(
                e, self
            )
            for e in self.input
        ]
