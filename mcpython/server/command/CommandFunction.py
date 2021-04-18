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
from mcpython.server.command.Builder import Command, CommandNode, AnyString
from mcpython import shared


function = Command("function").than(
    CommandNode(AnyString.INSTANCE)
    .of_name("function")
    .info("invokes the function given")
    .on_execution(lambda env, data: shared.command_parser.run_function(data[1], env))
)
