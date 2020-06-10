"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.chat.command.Command
from mcpython.chat.command.Command import ParseType, ParseMode, SubCommand, ParseBridge


@G.registry
class CommandGamerule(mcpython.chat.command.Command.Command):
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

