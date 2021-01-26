"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.common.DataPack
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    CommandArgumentMode,
    Node,
)


@shared.registry
class CommandFunction(mcpython.server.command.Command.Command):
    """
    command /function
    """

    NAME = "minecraft:function_command"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "function"
        command_syntax_holder.add_node(
            Node(
                CommandArgumentType.STRING_WITHOUT_QUOTES,
                mode=CommandArgumentMode.OPTIONAL,
            )
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        mcpython.common.DataPack.datapack_handler.try_call_function(values[0], info)
        # todo: make self-calling save [sub-function calls are possible! -> move to an "execute"-stack]

    @staticmethod
    def get_help() -> list:
        return ["/function <name>: runs the function named name from an datapack"]
