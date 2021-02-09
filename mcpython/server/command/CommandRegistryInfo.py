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
from mcpython import shared, logger
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    Node,
)


@shared.registry
class CommandRegistryInfo(mcpython.server.command.Command.Command):
    """
    command /registryinfo
    """

    NAME = "minecraft:registry_info"

    CANCEL_REGISTRY_INFO = False

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "registryinfo"
        command_syntax_holder.add_node(Node(CommandArgumentType.STRING_WITHOUT_QUOTES))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if not shared.event_handler.call_cancelable(
            "commands:registryinfo", values[0], info
        ):
            return
        registry = shared.registry.get_by_name(values[0])

        # todo: add extension point for mods with custom registries
        # todo: add option to hide registries from this in the registry

        if registry is None:
            logger.println(
                "[CHAT][ERROR] selected unknown registry: '{}'".format(values[0])
            )
            return

        if len(values) == 1:
            logger.println("values in registry '{}'".format(values[0]))
            for key in registry.entries.keys():
                element = registry.entries[key]
                logger.println(key, element, element.INFO, sep=" ")

    @staticmethod
    def get_help() -> list:
        return [
            "/registryinfo <registry> [<attribute>]: gives info to selected registry"
        ]
