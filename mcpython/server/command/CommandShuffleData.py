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
import mcpython.common.container.ItemStack
from mcpython.server.command.Command import ParseBridge
import mcpython.common.config


@shared.registry
class CommandShuffleData(mcpython.server.command.Command.Command):
    """
    class for /shuffledata command
    """

    NAME = "minecraft:shuffle_data_command"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "shuffledata"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if not mcpython.common.config.SHUFFLE_DATA:
            info.chat.print_ln("can't shuffle data as shuffeling is disabled")
            return
        shared.event_handler.call("data:shuffle:all")

    @staticmethod
    def get_help() -> list:
        return ["/shuffledata: will shuffle a lot of data when enabled in configs"]
