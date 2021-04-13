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
import mcpython.util.math
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    CommandArgumentMode,
    Node,
)


@shared.registry
class CommandGenerate(mcpython.server.command.Command.Command):
    """
    class for /generate command
    """

    NAME = "minecraft:generate"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "generate"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.INT, mode=CommandArgumentMode.OPTIONAL).add_node(
                Node(CommandArgumentType.INT).add_node(
                    Node(
                        CommandArgumentType.INT, mode=CommandArgumentMode.OPTIONAL
                    ).add_node(Node(CommandArgumentType.INT))
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        dim = info.entity.dimension
        if len(values) > 0:  # have we definite an chunk?
            chunk_start = tuple(values[:2])
            chunk_end = tuple(values[2:]) if len(values) > 2 else chunk_start
        else:
            chunk_start = chunk_end = mcpython.util.math.position_to_chunk(
                shared.world.get_active_player().position
            )
        fx, fz = chunk_start
        tx, tz = chunk_end
        if fx > tx:
            fx, tx = tx, fx
        if fz > tz:
            fz, tz = tz, fz
        for x in range(fx, tx + 1):
            for z in range(fz, tz + 1):
                c = dim.get_chunk(x, z, generate=False)
                shared.world_generation_handler.add_chunk_to_generation_list(c)
                # only generate the ones from us todo: add option to runtime-generate
                shared.world_generation_handler.task_handler.process_tasks(chunks=[c])

    @staticmethod
    def get_help() -> list:
        return [
            "/generate [<x> <z> [<tox> <toz>]]: generates the chunk you are in if no one is specified or the "
            "specified area, else the specified chunk by (x, z)"
        ]
