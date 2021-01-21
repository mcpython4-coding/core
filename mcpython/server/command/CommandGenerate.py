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
import mcpython.util.math
from mcpython.server.command.Command import (
    ParseBridge,
    ParseType,
    ParseMode,
    SubCommand,
)


@shared.registry
class CommandGenerate(mcpython.server.command.Command.Command):
    """
    class for /generate command
    """

    NAME = "minecraft:generate"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "generate"
        parsebridge.add_subcommand(
            SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL).add_subcommand(
                SubCommand(ParseType.INT).add_subcommand(
                    SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL).add_subcommand(
                        SubCommand(ParseType.INT)
                    )
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        dim = info.entity.dimension
        if len(values) > 0:  # have we definite an chunk?
            chunkf = tuple(values[:2])
            chunkt = tuple(values[2:]) if len(values) > 2 else chunkf
        else:
            chunkf = chunkt = mcpython.util.math.position_to_chunk(
                shared.world.get_active_player().position
            )
        fx, fz = chunkf
        tx, tz = chunkt
        if fx > tx:
            fx, tx = tx, fx
        if fz > tz:
            fz, tz = tz, fz
        for x in range(fx, tx + 1):
            for z in range(fz, tz + 1):
                c = dim.get_chunk(x, z, generate=False)
                shared.world_generation_handler.add_chunk_to_generation_list(c)
                shared.world_generation_handler.task_handler.process_tasks(
                    chunks=[c]
                )  # only generate the ones from us

    @staticmethod
    def get_help() -> list:
        return [
            "/generate [<x> <z> [<tox> <toz>]]: generates the chunk you are in if no one is specified or the "
            "specified area, else the specified chunk by (x, z)"
        ]
