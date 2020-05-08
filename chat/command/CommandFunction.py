"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import chat.DataPack


@G.registry
class CommandFunction(chat.command.Command.Command):
    """
    command /function
    """

    NAME = "minecraft:function_command"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "function"
        parsebridge.add_subcommand(SubCommand(ParseType.STRING_WITHOUT_QUOTES, mode=ParseMode.OPTIONAL))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        chat.DataPack.datapackhandler.try_call_function(values[0], info)
        # todo: make self-calling save [sub-function calls are possible! -> move to an "execute"-stack]

    @staticmethod
    def get_help() -> list:
        return ["/function <name>: runs the function named name from an datapack"]

