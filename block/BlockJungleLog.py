"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from .ILog import ILog


@G.registry
class BlockJungleLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:jungle_log"


@G.registry
class BlockStrippedJungleLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_jungle_log"


@G.registry
class BlockJungleWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:jungle_wood"


@G.registry
class BlockStrippedJungleWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_jungle_wood"

