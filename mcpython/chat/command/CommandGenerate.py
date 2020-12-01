"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
import mcpython.chat.command.Command
import mcpython.util.math
from mcpython.chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandGenerate(mcpython.chat.command.Command.Command):
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
            chunkf = chunkt = mcpython.util.math.positionToChunk(G.world.get_active_player().position)
        fx, fz = chunkf
        tx, tz = chunkt
        if fx > tx: fx, tx = tx, fx
        if fz > tz: fz, tz = tz, fz
        for x in range(fx, tx+1):
            for z in range(fz, tz+1):
                c = dim.get_chunk(x, z, generate=False)
                G.worldgenerationhandler.add_chunk_to_generation_list(c)
                G.worldgenerationhandler.task_handler.process_tasks(chunks=[c])  # only generate the ones from us

    @staticmethod
    def get_help() -> list:
        return ["/generate [<x> <z> [<tox> <toz>]]: generates the chunk you are in if no one is specified or the "
                "specified area, else the specified chunk by (x, z)"]

