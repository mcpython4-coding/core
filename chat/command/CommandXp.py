"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandClear(chat.command.Command.Command):
    """
    command /clear
    """

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["xp", "experience"]
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "add").add_subcommand(
            SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(ParseType.INT).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "points", mode=ParseMode.OPTIONAL)
            ).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "levels", mode=ParseMode.OPTIONAL)
            ))
        )).add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "set").add_subcommand(
            SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(ParseType.INT).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "points", mode=ParseMode.OPTIONAL)
            ).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "levels", mode=ParseMode.OPTIONAL)
            ))
        ))

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][1] in [0, 1]:
            if modes[1][1] == 1:
                G.player.xp = 0
                G.player.xp_level = 0
            if len(modes) == 4 or modes[4][1] == 0:  # points
                for player in values[1]:
                    player.add_xp(values[2])
            elif modes[4][1] == 1:  # levels
                for player in values[1]:
                    player.add_xp_level(values[2])

    @staticmethod
    def get_help() -> list:
        return ["/xp add <selector> <level> [points|levels]: add xp to entity",
                "/xp set <selector> <level> [points|levels]: set xp level of entity"]

