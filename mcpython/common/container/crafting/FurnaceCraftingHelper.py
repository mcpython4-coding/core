"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.container.crafting.IRecipe
from mcpython import shared
import mcpython.common.container.crafting.GridRecipeInstances


@shared.crafting_handler
class FurnaceRecipe(mcpython.common.container.crafting.IRecipe.IRecipe):
    """
    Interface for decoding an furnace-like recipe
    """

    # The list of type descriptors to decode
    RECIPE_NAMES = ["minecraft:smelting", "minecraft:blasting", "minecraft:smoking"]

    @classmethod
    def from_data(cls, data: dict, file: str) -> "FurnaceRecipe":
        """
        Loader function for an furnace crafting recipe
        :param data: the data to load
        :param file: the file loaded from
        :return: the recipe instance created
        """
        inputs = [
            x[0]
            for x in mcpython.common.container.crafting.GridRecipeInstances.transform_to_item_stack(
                data["ingredient"], file
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
            shared.crafting_handler.furnace_recipes.setdefault(
                self.type, {}
            ).setdefault(e, self)
            for e in self.input
        ]
