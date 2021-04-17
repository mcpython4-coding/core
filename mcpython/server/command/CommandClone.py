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
import mcpython.common.world.util


# todo: full command here!
clone = Command("clone").than(
    CommandNode(IntPosition())
    .of_name("start")
    .than(
        CommandNode(IntPosition())
        .of_name("end")
        .than(
            CommandNode(IntPosition())
            .of_name("target")
            .info("clones the given area to the given target")
            .on_execution(
                lambda env, data: mcpython.common.world.util.clone(
                    env.get_dimension(), data[1], data[2], data[3]
                )
            )
        )
    )
)
