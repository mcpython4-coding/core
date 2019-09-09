"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import util.math


@G.registry
class CommandGenerate(chat.command.Command.Command):
    """
    class for /generate command
    """
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "generate"
        parsebridge.add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.INT).add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL).add_subcommand(
                                                     SubCommand(ParseType.INT)))))

    @staticmethod
    def parse(values: list, modes: list, info):
        dim = G.world.get_active_dimension()
        if len(values) > 0:  # have we definite an chunk?
            chunkf = tuple(values[:2])
            chunkt = tuple(values[2:]) if len(values) > 2 else chunkf
        else:
            chunkf = chunkt = util.math.sectorize(G.window.position)
        fx, fz = chunkf
        tx, tz = chunkt
        if fx > tx: fx, tx = tx, fx
        if fz > tz: fz, tz = tz, fz
        for x in range(fx, tx):
            for z in range(fz, tz):
                G.worldgenerationhandler.generate_chunk(dim.get_chunk(x, z, generate=False))
        G.world.process_entire_queue()

    @staticmethod
    def get_help() -> list:
        return ["/generate [<x> <z> [<tox> <toz>]]: generates the chunk you are in if no one is specified or the "
                "specified area, else the specified"]

