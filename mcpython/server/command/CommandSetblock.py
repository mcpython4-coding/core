from mcpython.server.command.Builder import (
    Command,
    CommandNode,
    IntPosition,
    Block,
)
from mcpython import shared


setblock = Command("setblock").than(
    CommandNode(IntPosition())
    .of_name("position")
    .than(
        CommandNode(Block())
        .of_name("block")
        .on_execution(lambda env, data: print(data[1]))
        .info("Sets a given block at the given position")
    )
)

shared.command_parser.register_command(setblock)
