"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import mcpython.chat.command.Command
from mcpython.chat.command.Command import ParseBridge, ParseType, SubCommand


@G.registry
class CommandTell(mcpython.chat.command.Command.Command):
    """
    command /tell, /msg and /w
    """

    NAME = "minecraft:tell"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["tell", "msg", "w"]
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(
            ParseType.OPEN_END_UNDEFINITED_STRING)))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        msg = " ".join(values[1])
        for entity in values[0]:
            entity.tell(msg)

    @staticmethod
    def get_help() -> list:
        return ["/tell <selector> <msg>: tells an player an message",
                "/msg <selector> <msg>: tells an player an message",
                "/w <selector> <msg>: tells an player an message"]

