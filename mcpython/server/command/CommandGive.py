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
from mcpython.server.command.Builder import Command, CommandNode, Selector, Item, Int
from mcpython import shared


def give_helper(entities, item, count):
    if len(entities) > 0:
        import mcpython.common.container.ResourceStack

        stack = mcpython.common.container.ResourceStack.ItemStack(item, count)

        entities[0].pick_up_item(stack)


give = Command("give").than(
    CommandNode(Selector(max_entities=1))
    .of_name("to whom")
    .than(
        CommandNode(Item())
        .of_name("item")
        .on_execution(lambda env, data: give_helper(data[1](env), data[2], 1))
        .info("Gives the selected entity one item")
        .than(
            CommandNode(Int(only_positive=True, include_zero=True))
            .of_name("count")
            .on_execution(lambda env, data: give_helper(data[1](env), data[2], data[3]))
            .info("Gives the selected entity <amount> items")
        )
    )
)
