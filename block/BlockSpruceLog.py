"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from .ILog import ILog


@G.registry
class BlockSpruceLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:spruce_log"


@G.registry
class BlockStrippedSpruceLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_spruce_log"


@G.registry
class BlockSpruceWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:spruce_wood"


@G.registry
class BlockStrippedSpruceWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_spruce_wood"

