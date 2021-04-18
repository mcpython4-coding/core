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
    Position,
)
from mcpython import shared


teleport = (
    Command("teleport")
    .alias("tp")
    .than(
        CommandNode(Selector())
        .of_name("entity")
        .than(
            CommandNode(Position())
            .of_name("target position")
            .info("teleports the given entities to the given position")
            .on_execution(
                lambda env, data: [
                    entity.teleport(data[2](env)[0], env.get_dimension())
                    for entity in data[1](env)
                ]
            )
        )
    )
    .than(
        CommandNode(Position())
        .of_name("target")
        .info("teleports the current entity to the given position")
        .on_execution(
            lambda env, data: env.get_this().teleport(
                data[1](env)[0], env.get_dimension()
            )
        )
    )
)
