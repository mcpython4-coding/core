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


def clear_helper(entities):
    for entity in entities:
        for inventory in entity.get_inventories():
            inventory.clear()
        entity.on_inventory_cleared()


clear = (
    Command("clear")
    .than(
        CommandNode(Selector())
        .of_name("target")
        .on_execution(lambda env, data: clear_helper(data[1](env)))
        .info("clears the inventory of all entities of target")
    )
    .on_execution(lambda env, data: clear_helper((env.get_this(),)))
    .info("Clears the inventory of the executing entity")
)
