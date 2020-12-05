"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import uuid


class IRecipe:
    @staticmethod
    def get_recipe_names() -> list:  # todo: make attribute
        raise NotImplementedError()

    @classmethod
    def from_data(cls, data: dict):
        return cls()

    def __init__(self):
        self.uuid = uuid.uuid4()
        self.name = None

    def register(self):
        pass