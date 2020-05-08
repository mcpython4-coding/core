"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import util.math


@G.registry
class CommandSetblock(chat.command.Command.Command):
    """
    class for /setblock command
    """

    NAME = "minecraft:setblock"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "setblock"
        parsebridge.add_subcommand(SubCommand(ParseType.POSITION).add_subcommand(SubCommand(ParseType.BLOCKNAME)))

    @staticmethod
    def parse(values: list, modes: list, info):
        G.world.dimensions[info.dimension].add_block(util.math.normalize(values[0]), values[1])

    @staticmethod
    def get_help() -> list:
        return ["/setblock <position> <blockname>"]

