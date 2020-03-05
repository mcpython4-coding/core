"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import uuid


class IRecipe:
    @staticmethod
    def get_recipe_names() -> list:
        raise NotImplementedError()

    @classmethod
    def from_data(cls, data: dict):
        return cls()

    def __init__(self):
        self.uuid = uuid.uuid4()

    def register(self):
        pass

