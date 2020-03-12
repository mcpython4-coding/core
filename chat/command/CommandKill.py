"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandKill(chat.command.Command.Command):
    """
    class for /kill command
    """

    NAME = "minecraft:kill"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "kill"
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL))

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0: values.append([G.world.get_active_player()])
        for entity in values[0]:
            entity.kill(test_totem=False)  # kill all entities selected

    @staticmethod
    def get_help() -> list:
        return ["/kill [<selector>: default=@s]: kills entity(s)"]

