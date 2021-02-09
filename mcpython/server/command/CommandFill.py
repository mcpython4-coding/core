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
class CommandFill(mcpython.server.command.Command.Command):
    """
    class for /fill command
    """

    NAME = "minecraft:fill"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "fill"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.POSITION).add_node(
                Node(CommandArgumentType.POSITION).add_node(
                    Node(CommandArgumentType.BLOCK_NAME).add_node(
                        Node(
                            CommandArgumentType.DEFINED_STRING,
                            mode=CommandArgumentMode.OPTIONAL,
                        ).add_node(CommandArgumentType.BLOCK_NAME)
                    )
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        replace = None if len(values) == 3 else values[4]
        dimension = shared.world.dimensions[info.dimension]
        # sort positions so that pos1 < pos2
        (fx, fy, fz), (tx, ty, tz) = tuple(values[:2])
        if fx > tx:
            tx, fx = fx, tx
        if fy > ty:
            ty, fy = fy, ty
        if fz > tz:
            tz, fz = fz, tz
        # iterate over all blocks
        positions = []
        for x in range(round(fx), round(tx) + 1):
            for y in range(round(fy), round(ty) + 1):
                for z in range(round(fz), round(tz) + 1):
                    block = dimension.get_block((x, y, z))
                    if not replace or (
                        block and block.NAME == replace
                    ):  # check for replace block
                        chunk = dimension.get_chunk_for_position((x, y, z))
                        chunk.add_block((x, y, z), values[2], block_update=False)
                        positions.append((chunk, (x, y, z)))
        for chunk, position in positions:
            chunk.on_block_updated(position)

    @staticmethod
    def get_help() -> list:
        return ["/fill <from> <to> <block> [replace <blockname>]"]
