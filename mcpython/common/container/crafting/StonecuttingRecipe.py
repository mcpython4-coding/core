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
import typing

import mcpython.common.container.crafting.IRecipe
from mcpython import shared


@shared.crafting_handler
class StoneCuttingRecipe(mcpython.common.container.crafting.IRecipe.IRecipe):
    # The list of type descriptors to decode
    RECIPE_TYPE_NAMES = ["minecraft:stonecutting"]
    CRAFTING_SUPPORT = ["minecraft:stonecutter"]

    RECIPES: typing.Dict[str, typing.List["StoneCuttingRecipe"]] = {}

    @classmethod
    def from_data(cls, data: dict, file: str) -> "StoneCuttingRecipe":
        return cls(
            data["ingredient"]["item"], data["result"], data.setdefault("count", 1)
        )

    def __init__(self, ingredient: str, result: str, count: int = 1):
        super().__init__()
        self.ingredient = ingredient
        self.result = result
        self.count = count

    async def prepare(self):
        StoneCuttingRecipe.RECIPES.setdefault(self.ingredient, []).append(self)
