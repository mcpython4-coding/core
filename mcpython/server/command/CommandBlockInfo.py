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
    """

    NAME = "minecraft:block_info"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "blockinfo"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        # x, y, z = info.entity.position
        # nx, ny, nz = mcpython.util.math.normalize(info.entity.position)
        # chunk = info.dimension.get_chunk(
        #     *mcpython.util.math.position_to_chunk(info.entity.position),
        #     create=False
        # )
        vector = shared.window.get_sight_vector()
        blockpos, previous, hitpos = shared.world.hit_test(info.entity.position, vector)
        if blockpos:
            block = shared.world.get_dimension(info.dimension).get_block(blockpos)
            if type(block) == str:
                logger.println("invalid target")
            else:
                logger.println(repr(block))
                logger.println(block.TAGS)
        else:
            logger.println("invalid target")

    @staticmethod
    def get_help() -> list:
        return ["/blockinfo: prints info about the block looking at"]
