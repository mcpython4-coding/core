"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.server.command.Command
import mcpython.common.container.ItemStack
from mcpython.server.command.Command import (
    ParseType,
    ParseMode,
    SubCommand,
    ParseBridge,
)


@G.registry
class CommandGive(mcpython.server.command.Command.Command):
    """
    class for /give command
    """

    NAME = "minecraft:give"

    CANCEL_GIVE = False

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.add_subcommand(
            SubCommand(ParseType.SELECTOR).add_subcommand(
                SubCommand(ParseType.ITEMNAME).add_subcommand(
                    SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL)
                )
            )
        )
        parsebridge.main_entry = "give"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        stack = mcpython.common.container.ItemStack.ItemStack(
            values[1]
        )  # get the stack to add
        if len(values) > 2:
            stack.amount = abs(values[2])  # get the amount if provided
        # check for overflow
        if stack.amount > stack.item.STACK_SIZE:
            stack.amount = stack.item.STACK_SIZE
        for player in values[0]:  # iterate over all players to give
            player.pick_up_item(stack)

    @staticmethod
    def get_help() -> list:
        return ["/give <selector> <item> [<amount>: default=1]: gives items"]
