"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import util.math


@G.commandhandler
class CommandReload(chat.command.Command.Command):
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "generate"
        parsebridge.add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.INT)))

    @staticmethod
    def parse(values: list, modes: list, info):
        dim = G.world.get_active_dimension()
        if len(values) > 0:
            chunkp = tuple(values)
        else:
            chunkp = util.math.sectorize(G.window.position)
        G.worldgenerationhandler.generate_chunk(dim.get_chunk(*chunkp, generate=False))
        G.world.process_entire_queue()

    @staticmethod
    def get_help() -> list:
        return ["/generate [<x> <z>]: generates the chunk you are in if no one is specified, else the specified"]

