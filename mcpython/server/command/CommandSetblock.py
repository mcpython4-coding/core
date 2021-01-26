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
import mcpython.util.math
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    Node,
)


@shared.registry
class CommandSetblock(mcpython.server.command.Command.Command):
    """
    class for /setblock command
    """

    NAME = "minecraft:setblock"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "setblock"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.POSITION).add_node(
                Node(CommandArgumentType.BLOCK_NAME)
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        position = mcpython.util.math.normalize(values[0])
        shared.world.dimensions[info.dimension].get_chunk_for_position(
            position
        ).add_block(position, values[1])

    @staticmethod
    def get_help() -> list:
        return ["/setblock <position> <blockname>"]
