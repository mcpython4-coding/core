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
    class for /kill command
    """

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "kill"
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL))

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0: values.append([G.player])
        for entity in values[0]:
            entity.kill()  # kill all entities selected

    @staticmethod
    def get_help() -> list:
        return ["/kill [<selector>: default=@s]: kills entity(s)"]

