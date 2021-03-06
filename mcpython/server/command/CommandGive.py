"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.server.command.Command
import mcpython.common.container.ItemStack
from mcpython.server.command.Command import (
    CommandArgumentType,
    CommandArgumentMode,
    Node,
    CommandSyntaxHolder,
)


@shared.registry
class CommandGive(mcpython.server.command.Command.Command):
    """
    class for /give command
    """

    NAME = "minecraft:give"

    CANCEL_GIVE = False

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.add_node(
            Node(CommandArgumentType.SELECTOR).add_node(
                Node(CommandArgumentType.ITEM_NAME).add_node(
                    Node(CommandArgumentType.INT, mode=CommandArgumentMode.OPTIONAL)
                )
            )
        )
        command_syntax_holder.main_entry = "give"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        # get the stack to add
        stack = mcpython.common.container.ItemStack.ItemStack(values[1])

        if len(values) > 2:
            stack.set_amount(values[2])  # get the amount if provided

        for player in values[0]:  # iterate over all players to give
            player.pick_up_item(stack)

    @staticmethod
    def get_help() -> list:
        return ["/give <selector> <item> [<amount>: default=1]: gives items"]
