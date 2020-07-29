"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import mcpython.chat.command.Command
import mcpython.gui.ItemStack
from mcpython.chat.command.Command import ParseType, ParseMode, SubCommand, ParseBridge


@G.registry
class CommandGive(mcpython.chat.command.Command.Command):
    """
    class for /give command
    """

    NAME = "minecraft:give"

    CANCEL_GIVE = False

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(
            ParseType.ITEMNAME).add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL))))
        parsebridge.main_entry = "give"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        stack = mcpython.gui.ItemStack.ItemStack(values[1])  # get the stack to add
        if len(values) > 2: stack.amount = abs(values[2])  # get the amount if provided
        # check for overflow
        if stack.amount > stack.item.STACK_SIZE: stack.amount = stack.item.STACK_SIZE
        for player in values[0]:  # iterate over all players to give
            player.pick_up(stack)

    @staticmethod
    def get_help() -> list:
        return ["/give <selector> <item> [<amount>: default=1]: gives items"]

