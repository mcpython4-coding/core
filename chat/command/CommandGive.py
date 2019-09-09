"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseType, ParseMode, SubCommand, ParseBridge
import gui.ItemStack


@G.registry
class CommandGive(chat.command.Command.Command):
    """
    class for /give command
    """

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(
            ParseType.ITEMNAME).add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL))))
        parsebridge.main_entry = "give"

    @staticmethod
    def parse(values: list, modes: list, info):
        stack = gui.ItemStack.ItemStack(values[1])  # get the stack to add
        if len(values) > 2: stack.amount = abs(values[2])  # get the amount if provided
        # check for overflow
        if stack.amount > stack.item.get_max_stack_size(): stack.amount = stack.item.get_max_stack_size()
        for player in values[0]:  # iterate over all players to give
            player.add_to_free_place(stack)

    @staticmethod
    def get_help() -> list:
        return ["/give <selector> <item> [<amount>: default=1]: gives items"]

