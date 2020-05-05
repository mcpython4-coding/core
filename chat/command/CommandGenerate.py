"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import util.math


@G.registry
class CommandGenerate(chat.command.Command.Command):
    """
    class for /generate command
    """
    NAME = "minecraft:generate"

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
            chunkf = chunkt = util.math.sectorize(G.world.get_active_player().position)
        fx, fz = chunkf
        tx, tz = chunkt
        if fx > tx: fx, tx = tx, fx
        if fz > tz: fz, tz = tz, fz
        for x in range(fx, tx+1):
            for z in range(fz, tz+1):
                G.worldgenerationhandler.generate_chunk(dim.get_chunk(x, z, generate=False))
        G.world.process_entire_queue()

    @staticmethod
    def get_help() -> list:
        return ["/generate [<x> <z> [<tox> <toz>]]: generates the chunk you are in if no one is specified or the "
                "specified area, else the specified"]

