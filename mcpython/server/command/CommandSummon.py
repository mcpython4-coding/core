"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    CommandArgumentMode,
    Node,
)


@shared.registry
class CommandSummon(mcpython.server.command.Command.Command):
    """
    command /summon
    """

    NAME = "minecraft:summon"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "summon"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.STRING_WITHOUT_QUOTES).add_node(
                Node(CommandArgumentType.POSITION, mode=CommandArgumentMode.OPTIONAL)
            )
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        position = values[1] if len(values) > 1 else info.entity.position
        # todo: add check if entity is summon-able by command
        # todo: add help
        # todo: add special command entry for entity type
        try:
            shared.entity_handler.spawn_entity(values[0], position, check_summon=True)
        except ValueError:
            logger.println(
                "[COMMAND][SUMMON] entity type '{}' not found!".format(values[0])
            )

    @staticmethod
    def get_help() -> list:
        return []
