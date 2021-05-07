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
from mcpython import logger, shared
from mcpython.server.command.Builder import (
    AnyString,
    Command,
    CommandNode,
    DefinedString,
)


def set_rule(name: str, state):
    shared.world.gamerule_handler.table[
        name
    ].status = shared.world.gamerule_handler.table[name].status.__class__(state)


gamerule = Command("gamerule").than(
    CommandNode(AnyString.INSTANCE)
    .of_name("rule")
    .info("gets the state of a given rule")
    .on_execution(
        lambda env, data: logger.println(
            f"rule {data[1]}: {shared.world.gamerule_handler.table[data[1]].status.status}"
        )
    )
    .than(
        CommandNode(AnyString.INSTANCE)
        .of_name("state")
        .info("sets the given rule to the given state")
        .on_execution(lambda env, data: set_rule(*data[1:]))
    )
)
