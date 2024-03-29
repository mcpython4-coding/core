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
import typing
from abc import ABC

import mcpython.common.event.api
import mcpython.common.event.Registry
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack


class IRecipe(mcpython.common.event.api.IRegistryContent, ABC):
    """
    Base class for recipes

    Data is matched by TYPE, than decoded by from_data() ['file' is for error messages]
    Later run the loading pipe, bake() is called
    After all that, prepare() is called. This should create the needed lookups for the crafting systems
    [e.g. maps from input -> output, ...]
    """

    __slots__ = ("name",)

    TYPE = "minecraft:recipe_type"
    RECIPE_TYPE_NAMES = []
    RECIPE_VIEW = None

    # item names supporting crafting operations of this recipe
    CRAFTING_SUPPORT = []

    @classmethod
    def from_data(cls, data: dict, file: str):
        raise NotImplementedError()

    def __init__(self):
        self.name = None

    def get_inputs(self) -> typing.Iterable[ItemStack]:
        return tuple()

    def get_outputs(self) -> typing.Iterable[ItemStack]:
        return tuple()

    async def bake(self):
        pass

    async def prepare(self):
        pass

    async def prepare_static(self):
        await shared.crafting_handler.add_recipe(self)
        shared.crafting_handler.static_recipes.append(self)
