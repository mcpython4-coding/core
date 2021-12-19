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

import mcpython.common.container.crafting.GridRecipeInstances
import mcpython.common.container.crafting.IRecipe
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack

from .GridRecipeInstances import transform_to_item_stack


@shared.crafting_handler
class SmithingRecipe(mcpython.common.container.crafting.IRecipe.IRecipe):
    __slots__ = mcpython.common.container.crafting.IRecipe.IRecipe.__slots__ + (
        "base",
        "addition",
        "output",
    )

    # The list of type descriptors to decode
    RECIPE_TYPE_NAMES = ["minecraft:smithing"]
    CRAFTING_SUPPORT = ["minecraft:smithing_table"]

    @classmethod
    def from_data(cls, data: dict, file: str) -> "SmithingRecipe":
        output = transform_to_item_stack(data["result"], file)
        return cls(
            list(map(lambda e: e[0], transform_to_item_stack(data["base"], file))),
            list(map(lambda e: e[0], transform_to_item_stack(data["addition"], file))),
            output[0][0] if output else None,
        )

    def __init__(self, base: typing.List[str], addition: typing.List[str], output: str):
        super().__init__()
        self.base = base
        self.addition = addition
        self.output = output
