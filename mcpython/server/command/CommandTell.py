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
)


@shared.registry
class CommandTell(mcpython.server.command.Command.Command):
    """
    command /tell, /msg and /w
    """

    NAME = "minecraft:tell"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = ["tell", "msg", "w"]
        command_syntax_holder.add_node(
            Node(CommandArgumentType.SELECTOR).add_node(
                Node(CommandArgumentType.OPEN_END_UNDEFINED_STRING)
            )
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        msg = " ".join(values[1])
        for entity in values[0]:
            entity.tell(msg)

    @staticmethod
    def get_help() -> list:
        return [
            "/tell <selector> <msg>: tells an player an message",
            "/msg <selector> <msg>: tells an player an message",
            "/w <selector> <msg>: tells an player an message",
        ]
