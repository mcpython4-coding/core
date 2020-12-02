"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    ParseBridge,
    ParseType,
    ParseMode,
    SubCommand,
)


@G.registry
class CommandFill(mcpython.server.command.Command.Command):
    """
    class for /fill command
    """

    NAME = "minecraft:fill"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "fill"
        parsebridge.add_subcommand(
            SubCommand(ParseType.POSITION).add_subcommand(
                SubCommand(ParseType.POSITION).add_subcommand(
                    SubCommand(ParseType.BLOCKNAME).add_subcommand(
                        SubCommand(
                            ParseType.DEFINIED_STRING, mode=ParseMode.OPTIONAL
                        ).add_subcommand(ParseType.BLOCKNAME)
                    )
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        replace = None if len(values) == 3 else values[4]
        dimension = G.world.dimensions[info.dimension]
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
