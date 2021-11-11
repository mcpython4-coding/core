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
from abc import ABC

import mcpython.client.gui.Slot
import mcpython.common.container.crafting.IRecipe
import pyglet


class NotEnoughItemsException(Exception):
    pass


class AbstractRecipeViewRenderer(ABC):
    """
    Renderer system for displaying a recipe to the player in a JEI-like style
    """

    def copy(self):
        return type(self)()

    def prepare_for_recipe(
        self, recipe: mcpython.common.container.crafting.IRecipe.IRecipe
    ):
        raise NotImplementedError

    def draw(self, position: typing.Tuple[int, int], hovering_slot=None):
        raise NotImplementedError

    def add_to_batch(
        self, position: typing.Tuple[int, int], batch: pyglet.graphics.Batch
    ):
        raise NotImplementedError

    def get_rendering_size(self) -> typing.Tuple[int, int]:
        raise NotImplementedError

    def copy_into(self, helper, *itemstacks, creative=False):
        raise NotEnoughItemsException

    def get_slots(self):
        return tuple()

    def tick(self, dt: float):
        pass
