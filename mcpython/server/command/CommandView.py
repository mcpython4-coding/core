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
    DefinedString,
    AnyString,
)
from mcpython import shared


view = Command("view").than(
    CommandNode(DefinedString("recipe"))
    .of_name("recipe")
    .than(
        CommandNode(AnyString.INSTANCE)
        .of_name("recipe")
        .info("creates a view for the given recipe")
        .on_execution(lambda env, data: shared.crafting_handler.show_to_player(data[2]))
    )
).than(
    # todo: a real in-game view with scrollbar, and custom injection point for rendering,
    #   e.g. items with item texture, blocks with BlockItem, ...
    CommandNode(DefinedString("registry"))
    .of_name("registry")
    .than(
        CommandNode(AnyString.INSTANCE)
        .of_name("registry")
        .info("views the content of a registry")
        .on_execution(lambda env, data: shared.registry.print_content(data[2]))
    )
)
