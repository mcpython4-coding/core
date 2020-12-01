"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
import mcpython.chat.command.Command
from mcpython.chat.command.Command import ParseBridge, ParseType, SubCommand, ParseMode


@G.registry
class CommandGamemode(mcpython.chat.command.Command.Command):
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

