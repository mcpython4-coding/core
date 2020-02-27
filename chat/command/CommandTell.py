"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandTell(chat.command.Command.Command):
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

