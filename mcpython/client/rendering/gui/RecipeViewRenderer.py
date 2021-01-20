"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import typing
from abc import ABC

import pyglet
import mcpython.common.container.crafting.IRecipe
import mcpython.client.gui.Slot


class NotEnoughItemsException(Exception):
    pass


class AbstractRecipeViewRenderer(ABC):
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
