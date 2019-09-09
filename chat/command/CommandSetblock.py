"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import util.math


@G.registry
class CommandSetblock(chat.command.Command.Command):
    """
    class for /setblock command
    """

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

