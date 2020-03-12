"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, SubCommand, ParseMode


@G.registry
class CommandGamemode(chat.command.Command.Command):
    """
    class for /gamemode command
    """

    NAME = "minecraft:gamemode"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.add_subcommand(SubCommand(ParseType.SELECT_DEFINITED_STRING, "0", "1", "2", "3", "survival",
                                              "creative", "hardcore", "spectator").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.main_entry = "gamemode"

    @staticmethod
    def parse(values: list, modes: list, info):
        mode = values[0]
        if len(values) == 1:  # have we an selector?
            G.world.get_active_player().set_gamemode(mode)
        else:
            for player in values[1]:  # iterate through all players
                player.set_gamemode(mode)

    @staticmethod
    def get_help() -> list:
        return ["/gamemode <mode> [<selector>: default=@s]: set gamemode of entity(s)"]

