"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Biome
import world.gen.feature.OakTreeFeature


@G.biomehandler
class Plains(Biome.Biome):
    @staticmethod
    def get_name() -> str:
        return "minecraft:plains"

    @staticmethod
    def get_temperature() -> float:
        return .8

    @staticmethod
    def get_weight() -> int:
        return 20

    @staticmethod
    def get_height_range():
        return [30, 50]

    @staticmethod
    def get_trees() -> list:
        return [(world.gen.feature.OakTreeFeature.OakTreeNormalFeature, 600)]


G.biomehandler.add_biome_to_dim(0, "minecraft:plains")

