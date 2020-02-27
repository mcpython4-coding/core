"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseType, ParseMode, SubCommand, ParseBridge
import gui.ItemStack


@G.registry
class CommandGamerule(chat.command.Command.Command):
    """
    class for /gamerule command
    """

    NAME = "minecraft:gamerule"

    CANCEL_GIVE = False

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.add_subcommand(SubCommand(ParseType.STRING_WITHOUT_QUOTES).add_subcommand(SubCommand(
            ParseType.STRING_WITHOUT_QUOTES, mode=ParseMode.OPTIONAL)))
        parsebridge.main_entry = "gamerule"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        rule = values[0]
        if rule not in G.world.gamerulehandler.table:
            G.chat.print_ln("[SYNTAX][ERROR] gamerule '{}' not found".format(rule))
            return
        if len(values) > 1:
            value = values[1]
            if G.world.gamerulehandler.table[rule].status.is_valid_value(value):
                G.world.gamerulehandler.table[rule].status = G.world.gamerulehandler.table[rule].status.__class__(value)
            else:
                G.chat.print_ln("invalid value '{}' for gamerule '{}'".format(value, rule))
        else:
            G.chat.print_ln("value of gamerule '{}': {}".format(
                rule, G.world.gamerulehandler.table[rule].status.status))

    @staticmethod
    def get_help() -> list:
        return ["/gamerule <name> [<value>]"]

