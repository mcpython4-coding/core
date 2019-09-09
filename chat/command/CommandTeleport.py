"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandKill(chat.command.Command.Command):
    """
    class for /setblock command
    """

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["tp", "teleport"]  # both are valid
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(ParseType.SELECTOR)).
                                   add_subcommand(SubCommand(ParseType.POSITION))).\
            add_subcommand(SubCommand(ParseType.POSITION))

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][0] == 0:  # tp [selector]
            if modes[2][0] == 0:  # tp [selector] [selector]
                for entity in values[0]:
                    entity.position = tuple(values[1][0].position)
            else:  # tp [selector] [position]
                for entity in values[0]:
                    entity.position = tuple(values[1][0])
        else:  # tp [position]
            # print(values)
            G.window.position = tuple(values[0][0])

    @staticmethod
    def get_help() -> list:
        return ["/tp <selector> <position>: teleport given entity(s) to position",
                "/tp <position>: teleport executer to position",
                "/teleport <selector> <position>: teleport given entity(s) to position",
                "/teleport <position>: teleport executer to position"]

