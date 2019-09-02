"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G


class IRecipe:
    @staticmethod
    def get_recipe_name() -> str:
        raise NotImplementedError()

    @classmethod
    def from_data(cls, data: dict):
        return cls()

    def get_identification(self):
        raise NotImplementedError()

