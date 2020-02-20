"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import util.math


@G.registry
class CommandSetblock(chat.command.Command.Command):
    """
    class for /setblock command
    """

    NAME = "minecraft:setblock"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "setblock"
        parsebridge.add_subcommand(SubCommand(ParseType.POSITION).add_subcommand(SubCommand(ParseType.BLOCKNAME)))

    @staticmethod
    def parse(values: list, modes: list, info):
        G.world.dimensions[info.dimension].add_block(util.math.normalize(values[0]), values[1])

    @staticmethod
    def get_help() -> list:
        return ["/setblock <position> <blockname>"]

