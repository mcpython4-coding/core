"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.server.command.Command
import mcpython.util.math
from mcpython.server.command.Command import ParseBridge, ParseType, SubCommand


@G.registry
class CommandSetblock(mcpython.server.command.Command.Command):
    """
    class for /setblock command
    """

    NAME = "minecraft:setblock"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "setblock"
        parsebridge.add_subcommand(
            SubCommand(ParseType.POSITION).add_subcommand(
                SubCommand(ParseType.BLOCKNAME)
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        position = mcpython.util.math.normalize(values[0])
        G.world.dimensions[info.dimension].get_chunk_for_position(position).add_block(
            position, values[1], blockupdateself=False
        )

    @staticmethod
    def get_help() -> list:
        return ["/setblock <position> <blockname>"]