"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import typing
from abc import ABC

import mcpython.common.event.Registry
import json
from mcpython.common.container.ItemStack import ItemStack


class IRecipe(mcpython.common.event.Registry.IRegistryContent, ABC):
    """
    Base class for recipes

    Data is matched by TYPE, than decoded by from_data() ['file' is for error messages]
    Later run the loading pipe, bake() is called
    After all that, prepare() is called. This should create the needed lookups for the crafting systems
    [e.g. maps from input -> output, ...]
    """

    TYPE = "minecraft:recipe_type"
    RECIPE_TYPE_NAMES = []
    RECIPE_VIEW = None

    @classmethod
    def from_data(cls, data: dict, file: str):
        raise NotImplementedError()

    def __init__(self):
        self.name = None

    def get_inputs(self) -> typing.Iterable[ItemStack]:
        return tuple()

    def get_outputs(self) -> typing.Iterable[ItemStack]:
        return tuple()

    def bake(self):
        pass

    def prepare(self):
        pass
