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
)
from mcpython import shared


def clear(entities):
    for entity in entities:
        for inventory in entity.get_inventories():
            inventory.clear()
        entity.on_inventory_cleared()


setblock = (
    Command("clear")
    .than(
        CommandNode(Selector())
        .of_name("target")
        .on_execution(lambda env, data: clear(data[1](env)))
        .info("clears the inventory of all entities of target")
    )
    .on_execution(lambda env, data: clear((env.get_this(),)))
    .info("Clears the inventory of the executing entity")
)

shared.command_parser.register_command(setblock)
