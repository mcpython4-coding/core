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
)
from mcpython import shared
import enum


def gamemode_helper(mode, entities):
    for entity in entities:
        entity.set_gamemode(mode)


gamemode = Command("gamemode").than(
    CommandNode(
        DefinedString(
            "0",
            "1",
            "2",
            "3",
            "survival",
            "creative",
            "hardcore",
            "spectator",
        )
    )
    .of_name("mode")
    .on_execution(lambda env, data: gamemode_helper(data[1], (env.get_this(),)))
    .info("Sets the gamemode of the executing player")
    .than(
        CommandNode(Selector())
        .of_name("players")
        .info("Sets the gamemode of selected players")
        .on_execution(lambda env, data: gamemode_helper(data[1], data[2]))
    )
)
