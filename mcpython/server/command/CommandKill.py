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
from mcpython import shared
from mcpython.server.command.Builder import Command, CommandNode, Selector

kill = (
    Command("kill")
    .than(
        CommandNode(Selector(max_entities=1))
        .of_name("who")
        .on_execution(lambda env, data: [entity.kill() for entity in data[1](env)])
        .info("kills all selected entities")
    )
    .on_execution(lambda env, data: env.get_this().kill())
    .info("kills the executing entity")
)
