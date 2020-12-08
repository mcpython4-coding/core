"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython.server.command.CommandBuilder import (
    ICommandMatcher,
    CommandBuilder,
    ExecutingCommandInfo,
    PositionMatcher,
    TextMatcher,
    BlockPredicateMatcher,
    InvalidSyntaxError,
    FailType,
)
import mcpython.util.math
from mcpython import logger


def execute_clone(
    matcher: ICommandMatcher,
    builder: CommandBuilder,
    context: ExecutingCommandInfo,
    tree,
):
    start = tree[1].position
    end = tree[2].position
    target = tree[3].position

    fx, fy, fz = tuple([int(round(e)) for e in start])
    ex, ey, ez = tuple([int(round(e)) for e in end])

    # order them into the right order
    fx, ex = min(fx, ex), max(fx, ex)
    fy, ey = min(fy, ey), max(fy, ey)
    fz, ez = min(fz, ez), max(fz, ez)

    start = (fx, fy, fz)
    end = (ex, ey, ez)

    mode = get_mode_for_name(tree[-1].text) if tree[-1] in inner_matcher else NormalCloneMode
    if mode is None:
        context.chat.print_ln(
            "FATAL COMMAND ERROR: failed to parse clone mode {} ({}) as no mode handler is defined!".format(
                tree[-1].text, tree[-1]
            ))
        context.fail_execution(FailType.INTERNAL_FATAL, "ParserError register content")
        return
    mode.validate(start, end, target, tree)


class ICloneMode:
    NAME = None

    @classmethod
    def validate(cls, start, end, target, tree):
        pass


class ForceCloneMode(ICloneMode):
    NAME = "force"

    @classmethod
    def validate(cls, start, end, target, tree):
        pass


class MoveCloneMode(ICloneMode):
    NAME = "move"

    @classmethod
    def validate(cls, start, end, target, tree):
        pass


class NormalCloneMode(ICloneMode):
    NAME = "normal"

    @classmethod
    def validate(cls, start, end, target, tree):
        # todo: add some security checks here
        if mcpython.util.math.is_in_bounds(start, end, target):
            raise InvalidSyntaxError("area may NOT overlap with target area")


MODES = [ForceCloneMode, MoveCloneMode, NormalCloneMode]


def get_mode_for_name(name: str):
    for mode in MODES:
        if mode.NAME == name:
            return mode


# Matcher for inner part (force|move|normal)
inner_matcher = [
    TextMatcher("force").execute_on_end(execute_clone),
    TextMatcher("move").execute_on_end(execute_clone),
    TextMatcher("normal").execute_on_end(execute_clone),
]

clone = CommandBuilder("clone").add_subsequent_stage(
    PositionMatcher().add_subsequent_stage(
        PositionMatcher().add_subsequent_stage(
            PositionMatcher()
            .execute_on_end(execute_clone)
            .add_subsequent_stage(
                TextMatcher("replace")
                .execute_on_end(execute_clone)
                .add_subsequent_stages(inner_matcher)
            )
            .add_subsequent_stage(
                TextMatcher("masked")
                .execute_on_end(execute_clone)
                .add_subsequent_stages(inner_matcher)
            )
            .add_subsequent_stage(
                TextMatcher("filtered")
                .add_subsequent_stage(BlockPredicateMatcher())
                .execute_on_end(execute_clone)
                .add_subsequent_stages(inner_matcher)
            )
        )
    )
)


"""
@G.registry
class CommandClone(mcpython.server.command.old.Command.Command):

    @staticmethod
    def parse(values: list, modes: list, info):
        # todo: split up into three functions in an util/world.py for moving modes

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

        G.eventhandler.call("command:clone:block_map", info, block_map)

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
                block.face_state.update()

    @staticmethod
    def get_help() -> list:
        return [
            "/clone <edge 1> <edge 2> <to> [<mask mode>] [<clone mode>] [<tile name>]: clones an area"
        ]"""
