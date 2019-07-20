"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseType, ParseMode, SubCommand, ParseBridge
import gui.ItemStack


@G.commandhandler
class CommandGive(chat.command.Command.Command):
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(
            ParseType.ITEMNAME).add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL))))
        parsebridge.main_entry = "give"

    @staticmethod
    def parse(values: list, modes: list):
        stack = gui.ItemStack.ItemStack(values[1])
        if len(values) > 2: stack.amount = abs(values[2])
        values[0].add_to_free_place(stack)

