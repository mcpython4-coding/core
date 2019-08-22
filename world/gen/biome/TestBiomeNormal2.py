"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Biome


@G.biomehandler
class Test(Biome.Biome):
    @staticmethod
    def get_name() -> str:
        return "tests:biome:normal2"

    @staticmethod
    def get_temperature() -> float:
        return 0.

    @staticmethod
    def get_landmass() -> str:
        return "land"

    @staticmethod
    def get_weight() -> int:
        return 10


G.biomehandler.add_biome_to_dim(0, "tests:biome:normal2")

