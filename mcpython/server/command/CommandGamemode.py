"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    Node,
    CommandArgumentMode,
)


@shared.registry
class CommandGamemode(mcpython.server.command.Command.Command):
    """
    class for /gamemode command
    """

    NAME = "minecraft:gamemode"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.add_node(
            # todo: add config for values somewhere
            Node(
                CommandArgumentType.SELECT_DEFINED_STRING,
                "0",
                "1",
                "2",
                "3",
                "survival",
                "creative",
                "hardcore",
                "spectator",
            ).add_node(
                Node(CommandArgumentType.SELECTOR, mode=CommandArgumentMode.OPTIONAL)
            )
        )
        command_syntax_holder.main_entry = "gamemode"

    @staticmethod
    def parse(values: list, modes: list, info):
        mode = values[0]
        if len(values) == 1:  # have we an selector?
            shared.world.get_active_player().set_gamemode(mode)
        else:
            for player in values[1]:  # iterate through all players
                player.set_gamemode(mode)

    @staticmethod
    def get_help() -> list:
        return ["/gamemode <mode> [<selector>: default=@s]: set gamemode of entity(s)"]
