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
from mcpython.server.command.Command import ParseBridge, ParseType, SubCommand


@shared.registry
class CommandTeleport(mcpython.server.command.Command.Command):
    """
    class for /teleport command
    """

    NAME = "minecraft:teleport"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["tp", "teleport"]  # both are valid
        parsebridge.add_subcommand(
            SubCommand(ParseType.SELECTOR)
            .add_subcommand(SubCommand(ParseType.SELECTOR))
            .add_subcommand(SubCommand(ParseType.POSITION))
        ).add_subcommand(SubCommand(ParseType.POSITION))

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][0] == 0:  # tp [selector]
            if modes[2][0] == 0:  # tp [selector] [selector]
                for entity in values[0]:
                    entity.teleport(
                        tuple(values[1][0].position),
                        info.dimension
                        if info.dimension is not None
                        else entity.chunk.dimension.id,
                    )
            else:  # tp [selector] [position]
                for entity in values[0]:
                    entity.teleport(
                        tuple(values[1][0]),
                        info.dimension
                        if info.dimension is not None
                        else entity.chunk.dimension.id,
                    )
        else:  # tp [position]
            shared.world.get_active_player().teleport(
                tuple(values[0]),
                info.dimension
                if info.dimension is not None
                else shared.world.get_active_player().chunk.dimension.id,
            )

    @staticmethod
    def get_help() -> list:
        return [
            "/tp <selector> <position>: teleport given entity(s) to position",
            "/tp <position>: teleport executer to position",
            "/teleport <selector> <position>: teleport given entity(s) to position",
            "/teleport <position>: teleport executer to position",
        ]
