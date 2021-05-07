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
class StoneCuttingRecipe(mcpython.common.container.crafting.IRecipe.IRecipe):
    # todo: implement
    # The list of type descriptors to decode
    RECIPE_TYPE_NAMES = ["minecraft:stonecutting"]

    @classmethod
    def from_data(cls, data: dict, file: str) -> "StoneCuttingRecipe":
        pass
        return cls()

    def __init__(self):
        super().__init__()
