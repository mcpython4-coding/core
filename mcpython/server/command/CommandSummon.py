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
    Position,
    AnyString,
)
from mcpython import shared

summon = Command("summon").than(
    CommandNode(AnyString.INSTANCE)
    .of_name("entity type")
    .info("spawns the given entity at the current location")
    .on_execution(
        lambda env, data: shared.entity_handler.spawn_entity(
            data[1], env.get_position(), check_summon=True
        )
    )
    .with_handle(
        ValueError,
        lambda env, data, e: "[COMMAND][SUMMON] entity type '{}' not found!".format(
            data[1]
        ),
    )
    .than(
        CommandNode(Position())
        .of_name("position")
        .info("spawns the entity at the given position")
        .on_execution(
            lambda env, data: shared.entity_handler.spawn_entity(
                data[1], data[2], check_summon=True
            )
        )
        .with_handle(
            ValueError,
            lambda env, data, e: "[COMMAND][SUMMON] entity type '{}' not found!".format(
                data[1]
            ),
        )
    )
)
