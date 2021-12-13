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
import sys

import mcpython.engine.event.EventHandler
from mcpython import shared
from mcpython.server.command.Builder import Command, CommandNode, DefinedString

server = (
    Command("server", valid_on_integrated=False)
    .than(
        CommandNode(DefinedString("stop"))
        .of_name("stop")
        .info("stops the server")
        .on_execution(lambda env, data: sys.exit(-1))
    )
    .than(
        CommandNode(DefinedString("save"))
        .of_name("save")
        .info("saves the current world")
        .on_execution(lambda env, data: shared.world.save_file.save_world_async())
    )
)
