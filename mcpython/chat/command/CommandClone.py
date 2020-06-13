"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.chat.command.Command
from mcpython.chat.command.Command import ParseBridge, ParseType, ParseMode


@G.registry
class CommandClone(mcpython.chat.command.Command.Command):
    """
    class for /clone command
    """

    NAME = "minecraft:clone"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "clone"
        parsebridge.add_subcommand(ParseType.POSITION.add_subcommand(ParseType.POSITION.add_subcommand(
            ParseType.STRING_WITHOUT_QUOTES.set_mode(ParseMode.OPTIONAL).add_subcommand(
                ParseType.STRING_WITHOUT_QUOTES.set_mode(ParseMode.OPTIONAL).add_subcommand(
                    ParseType.BLOCKNAME.set_mode(ParseMode.OPTIONAL))))))

    @staticmethod
    def parse(values: list, modes: list, info):
        if 3 < len(values) < 6 and values[3] == "filtered":
            G.chat.print_ln("[SYNTAX][ERROR] when setting filtered, tile name must be set")
            return
        block_map = {}
        fx, fy, fz = tuple([round(e) for e in values[0]])
        ex, ey, ez = tuple([round(e) for e in values[1]])
        dx, dy, dz = tuple([round(e) for e in values[2]])
        # order them into the right order
        if fx > ex: ex, fx = fx, ex
        if fy > ey: ey, fy = fy, ey
        if fz > ez: ez, fz = fz, ez
        dimension = G.world.get_active_dimension()
        if len(values) > 4 and values[4] != "force" and fx <= dx <= ex and fy <= dy <= ey and fz <= dz <= ez:
            G.chat.print_ln("[CLONE][ERROR] can't clone in non-force mode an overlapping region")
            return
        # todo: split up into three functions in an util/world.py for moving modes
        for x in range(fx, ex+1):
            for y in range(fy, ey+1):
                for z in range(fz, ez+1):
                    rx, ry, rz = x - fx, y - fy, z - fz
                    block = dimension.get_block((x, y, z))
                    if type(block) == str: block = None
                    if len(values) == 3 or len(values) > 3 and values[3] == "normal":
                        block_map[(rx, ry, rz)] = block
                    elif len(values) > 3 and values[3] == "filtered" and block.NAME == values[5]:
                        block_map[(rx, ry, rz)] = block
                    elif len(values) > 3 and values[3] == "masked" and block is not None:
                        block_map[(rx, ry, rz)] = block
                    if len(values) > 4 and values[4] == "move":
                        dimension.remove_block((x, y, z))
        for x, y, z in block_map:
            chunk = dimension.get_chunk_for_position((x, y, z))
            if block_map[(x, y, z)] is None:
                chunk.remove_block((x, y, z))
            else:
                block = chunk.add_block((x+dx, y+dy, z+dz), block_map[(x, y, z)].NAME)
                block.set_model_state(block_map[(x, y, z)].get_model_state())
                block.face_state.update()

    @staticmethod
    def get_help() -> list:
        return ["/clone <edge 1> <edge 2> <to> [<mask mode>] [<clone mode>] [<tile name>]: clones an area"]

