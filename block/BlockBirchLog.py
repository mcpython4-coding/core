"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from .ILog import ILog


@G.blockhandler
class BlockBirchLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:birch_log"


@G.blockhandler
class BlockStrippedBirchLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_birch_log"


@G.blockhandler
class BlockBirchWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:birch_wood"


@G.blockhandler
class BlockStrippedBirchWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_birch_wood"

