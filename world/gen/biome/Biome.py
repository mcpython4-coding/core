"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G


class Biome:
    @staticmethod
    def get_name() -> str:
        raise NotImplementedError()

    @staticmethod
    def get_temperature() -> float:
        raise NotImplementedError()

    @staticmethod
    def get_landmass() -> str:
        return "land"

    @staticmethod
    def get_weight() -> int:
        return 10

    @staticmethod
    def get_high_range():
        return [10, 30]

    @staticmethod
    def get_top_layer_high_range():
        return [3, 5]

    @staticmethod
    def get_top_layer_configuration(high: int):
        return ["minecraft:dirt"] * (high - 1) + ["minecraft:grass_block"]
