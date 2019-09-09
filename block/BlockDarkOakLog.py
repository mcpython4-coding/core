"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from .ILog import ILog


@G.registry
class BlockDarkOakLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:dark_oak_log"


@G.registry
class BlockStrippedDarkOakLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_dark_oak_log"


@G.registry
class BlockDarkOakWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:dark_oak_wood"


@G.registry
class BlockStrippedDarkOakWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_dark_oak_wood"

