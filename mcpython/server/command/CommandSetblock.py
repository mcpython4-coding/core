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
    Block,
)


setblock = Command("setblock").than(
    CommandNode(IntPosition())
    .of_name("position")
    .than(
        CommandNode(Block())
        .of_name("block")
        .on_execution(lambda env, data: env.get_dimension().add_block(data[1], data[2]))
        .info("Sets a given block at the given position")
    )
)
