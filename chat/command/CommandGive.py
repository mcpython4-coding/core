"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
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
    def parse(values: list, modes: list, info):
        stack = gui.ItemStack.ItemStack(values[1])
        if len(values) > 2: stack.amount = abs(values[2])
        for player in values[0]:
            player.add_to_free_place(stack)

    @staticmethod
    def get_help() -> list:
        return ["/give <selector> <item> [<amount>: default=1]: gives items"]
