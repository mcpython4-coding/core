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
    CommandArgumentMode,
    Node,
)


@shared.registry
class CommandXp(mcpython.server.command.Command.Command):
    """
    command /xp
    """

    NAME = "minecraft:xp"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = ["xp", "experience"]
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "add").add_node(
                Node(CommandArgumentType.SELECTOR).add_node(
                    Node(CommandArgumentType.INT)
                    .add_node(
                        Node(
                            CommandArgumentType.DEFINED_STRING,
                            "points",
                            mode=CommandArgumentMode.OPTIONAL,
                        )
                    )
                    .add_node(
                        Node(
                            CommandArgumentType.DEFINED_STRING,
                            "levels",
                            mode=CommandArgumentMode.OPTIONAL,
                        )
                    )
                )
            )
        ).add_node(
            Node(CommandArgumentType.DEFINED_STRING, "set").add_node(
                Node(CommandArgumentType.SELECTOR).add_node(
                    Node(CommandArgumentType.INT)
                    .add_node(
                        Node(
                            CommandArgumentType.DEFINED_STRING,
                            "points",
                            mode=CommandArgumentMode.OPTIONAL,
                        )
                    )
                    .add_node(
                        Node(
                            CommandArgumentType.DEFINED_STRING,
                            "levels",
                            mode=CommandArgumentMode.OPTIONAL,
                        )
                    )
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][1] in [0, 1]:
            if modes[1][1] == 1:
                shared.world.get_active_player().xp = 0
                shared.world.get_active_player().xp_level = 0

            if len(modes) == 4 or modes[4][1] == 0:  # points
                for player in values[1]:
                    player.add_xp(values[2])

            elif modes[4][1] == 1:  # levels
                for player in values[1]:
                    player.add_xp_level(values[2])

    @staticmethod
    def get_help() -> list:
        return [
            "/xp add <selector> <level> [points|levels]: add xp to entity",
            "/xp set <selector> <level> [points|levels]: set xp level of entity",
        ]
