"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandFill(chat.command.Command.Command):
    """
    class for /fill command
    """
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "fill"
        parsebridge.add_subcommand(SubCommand(ParseType.POSITION).add_subcommand(
            SubCommand(ParseType.POSITION).add_subcommand(SubCommand(
                ParseType.BLOCKNAME).add_subcommand(SubCommand(ParseType.DEFINIED_STRING, mode=ParseMode.OPTIONAL).
                                                    add_subcommand(ParseType.BLOCKNAME)))))

    @staticmethod
    def parse(values: list, modes: list, info):
        replace = None if len(values) == 3 else values[4]
        dimension = G.world.dimensions[info.dimension]
        # sort positions so that pos1 < pos2
        (fx, fy, fz), (tx, ty, tz) = tuple(values[:2])
        if fx > tx: tx, fx = fx, tx
        if fy > ty: ty, fy = fy, ty
        if fz > tz: tz, fz = fz, tz
        # iterate over all blocks
        for x in range(round(fx), round(tx)+1):
            for y in range(round(fy), round(ty)+1):
                for z in range(round(fz), round(tz)+1):
                    block = dimension.get_block((x, y, z))
                    if not replace or (block and block.get_name() == replace):  # check for replace block
                        dimension.add_block((x, y, z), values[2])

    @staticmethod
    def get_help() -> list:
        return ["/fill <from> <to> <block> [replace <blockname>]"]

