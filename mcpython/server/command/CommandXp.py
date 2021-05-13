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
from mcpython.server.command.Builder import (Command, CommandNode,
                                             DefinedString, Int, Selector)

xp = (
    Command("xp")
    .alias("experience")
    .than(
        CommandNode(DefinedString("add"))
        .of_name("add")
        .than(
            CommandNode(Selector())
            .of_name("target")
            .than(
                CommandNode(
                    Int(only_positive=True)
                )  # todo: allow negative for removing XP
                .of_name("amount")
                .than(
                    CommandNode(DefinedString("points"))
                    .of_name("points")
                    .info("adds <amount> experience points to the selected players")
                    .on_execution(
                        lambda env, data: [
                            player.add_xp(data[3]) for player in data[2](env)
                        ]
                    )
                )
                .than(
                    CommandNode(DefinedString("levels"))
                    .of_name("levels")
                    .info("adds <amount> experience levels to the selected players")
                    .on_execution(
                        lambda env, data: [
                            player.add_xp_level(data[3]) for player in data[2](env)
                        ]
                    )
                )
            )
        )
    )
    .than(
        CommandNode(DefinedString("set"))
        .of_name("set")
        .than(
            CommandNode(Selector())
            .of_name("target")
            .than(
                CommandNode(Int(only_positive=True))
                .of_name("amount")
                .than(
                    CommandNode(DefinedString("points"))
                    .of_name("points")
                    .info("sets the experience of the selected players to <amount>")
                    .on_execution(
                        lambda env, data: [
                            player.clear_xp().add_xp(data[3]) for player in data[2](env)
                        ]
                    )
                )
                .than(
                    CommandNode(DefinedString("levels"))
                    .of_name("levels")
                    .info(
                        "sets the experience level of the selected players to <amount>"
                    )
                    .on_execution(
                        lambda env, data: [
                            player.clear_xp().add_xp_level(data[3])
                            for player in data[2](env)
                        ]
                    )
                )
            )
        )
    )
)
