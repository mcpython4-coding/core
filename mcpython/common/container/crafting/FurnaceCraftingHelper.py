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
import mcpython.common.container.crafting.GridRecipeInstances
import mcpython.common.container.crafting.IRecipe
from mcpython import shared


@shared.crafting_handler
class FurnaceRecipe(mcpython.common.container.crafting.IRecipe.IRecipe):
    """
    Interface for decoding an furnace-like recipe
    """

    CRAFTING_SUPPORT = [
        "minecraft:furnace",
        "minecraft:blast_furnace",
        "minecraft:smoker",
        "minecraft:campfire",
    ]

    # The list of type descriptors to decode
    RECIPE_TYPE_NAMES = [
        "minecraft:smelting",
        "minecraft:blasting",
        "minecraft:smoking",
        "minecraft:campfire_cooking",
    ]

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
            data["type"],
            inputs,
            result,
            data.setdefault("experience", 0),
            data["cookingtime"] / 20,
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
