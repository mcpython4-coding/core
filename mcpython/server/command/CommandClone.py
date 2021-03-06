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
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    CommandArgumentMode,
)


@shared.registry
class CommandClone(mcpython.server.command.Command.Command):
    """
    Class for the /clone command

    events:
        - command:clone:block_map(ParsingCommandInfo, dict): called when data is collected together with the data table
    """

    NAME = "minecraft:clone"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "clone"
        command_syntax_holder.add_node(
            CommandArgumentType.POSITION.add_node(
                CommandArgumentType.POSITION.add_node(
                    CommandArgumentType.STRING_WITHOUT_QUOTES.set_mode(
                        CommandArgumentMode.OPTIONAL
                    ).add_node(
                        CommandArgumentType.STRING_WITHOUT_QUOTES.set_mode(
                            CommandArgumentMode.OPTIONAL
                        ).add_node(
                            CommandArgumentType.BLOCK_NAME.set_mode(
                                CommandArgumentMode.OPTIONAL
                            )
                        )
                    )
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        # todo: split up into three functions in an util/world.py for moving modes
        # todo: raise error on float-positions

        if 3 < len(values) < 6 and values[3] == "filtered":
            info.chat.print_ln(
                "[SYNTAX][ERROR] when setting filtered, tile name must be set"
            )
            return
        block_map = {}  # the map holding the blocks to clone

        # parse the entries to their correct values
        fx, fy, fz = tuple([int(round(e)) for e in values[0]])
        ex, ey, ez = tuple([int(round(e)) for e in values[1]])
        dx, dy, dz = tuple([int(round(e)) for e in values[2]])

        # order them into the right order
        fx, ex = min(fx, ex), max(fx, ex)
        fy, ey = min(fy, ey), max(fy, ey)
        fz, ez = min(fz, ez), max(fz, ez)

        if (
            len(values) > 4
            and values[4] != "force"
            and fx <= dx <= ex
            and fy <= dy <= ey
            and fz <= dz <= ez
        ):
            info.chat.print_ln(
                "[CLONE][ERROR] can't clone in non-force mode an overlapping region"
            )
            return

        dimension = info.entity.dimension
        for x in range(fx, ex + 1):
            for y in range(fy, ey + 1):
                for z in range(fz, ez + 1):
                    rx, ry, rz = x - fx, y - fy, z - fz  # calculate the real position

                    chunk = dimension.get_chunk_for_position((rx, ry, rz))
                    block = chunk.get_block((x, y, z))  # and get the real block
                    if type(block) == str:
                        block = (
                            None  # if it is not generated yet, it is AIR for the moment
                        )

                    if len(values) == 3 or len(values) > 3 and values[3] == "normal":
                        block_map[(rx, ry, rz)] = block
                    elif (
                        len(values) > 3
                        and values[3] == "filtered"
                        and block.NAME == values[5]
                    ):
                        block_map[(rx, ry, rz)] = block
                    elif (
                        len(values) > 3 and values[3] == "masked" and block is not None
                    ):
                        block_map[(rx, ry, rz)] = block
                    if len(values) > 4 and values[4] == "move":
                        dimension.remove_block((x, y, z))

        shared.event_handler.call("command:clone:block_map", info, block_map)

        # and now iterate over the cached blocks...
        for x, y, z in block_map:
            chunk = dimension.get_chunk_for_position((x, y, z))

            # .. and update the position
            if block_map[(x, y, z)] is None:
                chunk.remove_block((x, y, z))
            else:
                block = chunk.add_block(
                    (x + dx, y + dy, z + dz), block_map[(x, y, z)].NAME
                )
                block.set_model_state(block_map[(x, y, z)].get_model_state())
                if shared.IS_CLIENT:
                    block.face_state.update()

    @staticmethod
    def get_help() -> list:
        return [
            "/clone <edge 1> <edge 2> <to> [<mask mode>] [<clone mode>] [<tile name>]: clones an area"
        ]
