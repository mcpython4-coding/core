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
    IntPosition,
)
from mcpython import shared


def block_info(env, position):
    if position is None:
        return

    block = env.get_dimension().get_block(position)
    if type(block) == str:
        env.chat.print_ln(f"invalid target; not generated at {position}")
    else:
        env.chat.print_ln(repr(block))
        env.chat.print_ln(", ".join(block.TAGS))


blockinfo = (
    Command("blockinfo")
    .than(
        CommandNode(IntPosition())
        .of_name("position")
        .on_execution(lambda env, data: block_info(env, data[1]))
        .info("Gives information about the given block")
    )
    .on_execution(
        lambda env, data: block_info(
            env,
            env.get_dimension()
            .get_world()
            .hit_test(env.get_this().get_position(), shared.window.get_sight_vector())[
                0
            ],
        )
    )
    .info("Gives information about the block looking at")
)
