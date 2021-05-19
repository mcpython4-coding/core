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
from mcpython.server.command.Builder import AnyString, Command, CommandNode, Selector

tell = (
    Command("tell")
    .alias("msg")
    .alias("w")
    .than(
        CommandNode(Selector())
        .of_name("target")
        .than(
            CommandNode(AnyString().open())
            .of_name("text")
            .info("sends the given text to the given entities")
            .on_execution(
                lambda env, data: [entity.tell(data[2]) for entity in data[1](env)]
            )
        )
    )
)
