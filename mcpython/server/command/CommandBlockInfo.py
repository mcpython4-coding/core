"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import ParseBridge
import mcpython.util.math


@shared.registry
class CommandBlockInfo(mcpython.server.command.Command.Command):
    """
    Class for the /blockinfo command
    todo: add variant for entities
    """

    NAME = "minecraft:block_info"

    @staticmethod
    def insert_parse_bridge(parse_bridge: ParseBridge):
        parse_bridge.main_entry = "blockinfo"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        # Which block do we want?
        blockpos, previous, hit_position = shared.world.hit_test(info.entity.position, shared.window.get_sight_vector())

        if blockpos:
            block = shared.world.get_dimension(info.dimension).get_block(blockpos)
            if type(block) == str:
                info.chat.print_ln("invalid target")
            else:
                info.chat.print_ln(repr(block))
                info.chat.print_ln(", ".join(block.TAGS))
        else:
            info.chat.print_ln("invalid target")

    @staticmethod
    def get_help() -> list:
        return ["/blockinfo: prints info about the block looking at, including a full repr() of it and its tags"]
