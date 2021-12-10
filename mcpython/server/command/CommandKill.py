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


async def kill_entities(env, data):
    for entity in data[1](env):
        await entity.kill()


async def kill_entity(env, data):
    await env.get_this().kill()


kill = (
    Command("kill")
    .than(
        CommandNode(Selector(max_entities=1))
        .of_name("who")
        .on_execution(kill_entities)
        .info("kills all selected entities")
    )
    .on_execution(kill_entity)
    .info("kills the executing entity")
)
