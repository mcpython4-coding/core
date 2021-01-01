"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    ParseBridge,
    ParseType,
    ParseMode,
    SubCommand,
)


@G.registry
class CommandSummon(mcpython.server.command.Command.Command):
    """
    command /summon
    """

    NAME = "minecraft:summon"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "summon"
        parsebridge.add_subcommand(
            SubCommand(ParseType.STRING_WITHOUT_QUOTES).add_subcommand(
                SubCommand(ParseType.POSITION, mode=ParseMode.OPTIONAL)
            )
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        position = values[1] if len(values) > 1 else info.entity.position
        # todo: add check if entity is summon-able by command
        try:
            G.entity_handler.spawn_entity(values[0], position, check_summon=True)
        except ValueError:
            logger.println(
                "[COMMAND][SUMMON] entity type '{}' not found!".format(values[0])
            )

    @staticmethod
    def get_help() -> list:
        return []
