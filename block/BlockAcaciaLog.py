"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from .ILog import ILog


@G.registry
class BlockAcaciaLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:acacia_log"


@G.registry
class BlockStrippedAcaciaLog(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_acacia_log"


@G.registry
class BlockAcaciaWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:acacia_wood"


@G.registry
class BlockStrippedAcaciaWood(ILog):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stripped_acacia_wood"

