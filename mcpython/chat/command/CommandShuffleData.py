"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
import mcpython.chat.command.Command
import mcpython.gui.ItemStack
from mcpython.chat.command.Command import ParseBridge
import mcpython.config


@G.registry
class CommandShuffleData(mcpython.chat.command.Command.Command):
    """
    class for /shuffledata command
    """

    NAME = "minecraft:shuffle_data_command"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "shuffledata"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if not mcpython.config.SHUFFLE_DATA:
            info.chat.print_ln("can't shuffle data as shuffeling is disabled")
            return
        G.eventhandler.call("data:shuffle:all")

    @staticmethod
    def get_help() -> list:
        return ["/shuffledata: will shuffle a lot of data when enabled in configs"]

