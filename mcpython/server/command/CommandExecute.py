"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython.server.command.Builder import (
    Command,
    CommandNode,
    Selector,
    DefinedString,
    AnyString,
    Position,
)
from mcpython import shared
import typing

"""
This is the complex command /execute <...>

It uses some special parsing
"""


# A list of CommandNodes representing all sub-parts of the system
command_chainable: typing.List[CommandNode] = []


class parts:
    run = (
        CommandNode(DefinedString("run"))
        .than(CommandNode(AnyString().open()))
        .info("runs the following command in the defined environment")
        .on_execution(lambda env, data: shared.command_parser.run(data[-1], env.copy()))
    )

    as_ = (
        CommandNode(DefinedString("as"))
        .than(CommandNode(Selector()))
        .than(CommandNode(AnyString().open()))
        .on_execution(
            lambda env, data: [
                shared.command_parser.run(data[-1], env.copy().with_this(entity))
                for entity in data[-2](env)
            ]
        )
    )
    at = (
        CommandNode(DefinedString("at"))
        .than(CommandNode(Position()))
        .than(CommandNode(AnyString().open()))
        .on_execution(
            lambda env, data: [
                shared.command_parser.run(data[-1], env.copy().with_position(pos))
                for pos in data[-2](env)
            ]
        )
    )
    in_ = (
        CommandNode(DefinedString("in"))
        .than(CommandNode(AnyString.INSTANCE))
        .than(AnyString().open())
        .on_execution(
            lambda env, data: shared.command_parser.run(
                data[-1], env.copy().with_dimension(data[-2])
            )
        )
    )
    # todo: if & unless


command_chainable += [
    parts.run,
    parts.as_,
    parts.at,
    parts.in_,
]


execute = Command("execute")
execute.following_nodes = command_chainable
