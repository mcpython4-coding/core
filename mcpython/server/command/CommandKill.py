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
    CommandSyntaxHolder,
    CommandArgumentType,
    CommandArgumentMode,
    Node,
)


@shared.registry
class CommandKill(mcpython.server.command.Command.Command):
    """
    class for /kill command
    """

    NAME = "minecraft:kill"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "kill"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.SELECTOR, mode=CommandArgumentMode.OPTIONAL)
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0:
            values.append([shared.world.get_active_player()])
        for entity in values[0]:
            entity.kill(test_totem=False)  # kill all entities selected

    @staticmethod
    def get_help() -> list:
        return ["/kill [<selector>: default=@s]: kills entity(s)"]
