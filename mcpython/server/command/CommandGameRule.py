"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    CommandArgumentType,
    CommandArgumentMode,
    Node,
    CommandSyntaxHolder,
)


@shared.registry
class CommandGamerule(mcpython.server.command.Command.Command):
    """
    class for /gamerule command
    """

    NAME = "minecraft:gamerule"

    CANCEL_GIVE = False

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.add_node(
            Node(CommandArgumentType.STRING_WITHOUT_QUOTES).add_node(
                Node(
                    CommandArgumentType.STRING_WITHOUT_QUOTES,
                    mode=CommandArgumentMode.OPTIONAL,
                )
            )
        )
        command_syntax_holder.main_entry = "gamerule"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        rule = values[0]
        if rule not in shared.world.gamerule_handler.table:
            shared.chat.print_ln("[SYNTAX][ERROR] gamerule '{}' not found".format(rule))
            return
        if len(values) > 1:
            value = values[1]
            if shared.world.gamerule_handler.table[rule].status.is_valid_value(value):
                shared.world.gamerule_handler.table[
                    rule
                ].status = shared.world.gamerule_handler.table[rule].status.__class__(
                    value
                )
            else:
                info.chat.print_ln(
                    "invalid value '{}' for gamerule '{}'".format(value, rule)
                )
        else:
            info.chat.print_ln(
                "value of gamerule '{}': {}".format(
                    rule, shared.world.gamerule_handler.table[rule].status.status
                )
            )

    @staticmethod
    def get_help() -> list:
        return ["/gamerule <name> [<value>]"]
