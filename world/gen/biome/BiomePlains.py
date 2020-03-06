"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Biome
import world.gen.feature.OakTreeFeature
import config


class Plains(Biome.Biome):
    NAME = "minecraft:plains"

    @staticmethod
    def get_temperature() -> float:
        return .8

    @staticmethod
    def get_weight() -> int:
        return 20

    @staticmethod
    def get_height_range():
        return config.BIOME_HEIGHT_RANGE_MAP["minecraft:plains"]

    @staticmethod
    def get_trees() -> list:
        return [(world.gen.feature.OakTreeFeature.OakTreeNormalFeature, 600)]


G.biomehandler.register(Plains, [0])

