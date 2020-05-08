"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

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

