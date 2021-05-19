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
import mcpython.common.DataPacks
from mcpython import shared
from mcpython.server.command.Builder import (AnyString, Command, CommandNode,
                                             DefinedString)

datapack = (
    Command("datapack")
    .than(
        CommandNode(DefinedString("enable")).than(
            CommandNode(AnyString.INSTANCE)
            .of_name("datapack")
            .info("enables the specified datapack")
            .on_execution(
                lambda env, data: mcpython.common.DataPacks.datapack_handler.enable_pack(
                    data[2]
                )
            )
        )
    )
    .than(
        CommandNode(DefinedString("disable")).than(
            CommandNode(AnyString.INSTANCE)
            .of_name("datapack")
            .info("disables the specified datapack")
            .on_execution(
                lambda env, data: mcpython.common.DataPacks.datapack_handler.disable_pack(
                    data[2]
                )
            )
        )
    )
    .than(
        CommandNode(DefinedString("list")).on_execution(
            lambda env, data: [
                env.chat.print_ln(f"- {pack.name}: {pack.status.name.lower()}")
                for pack in mcpython.common.DataPacks.datapack_handler.loaded_data_packs
            ]
        )
    )
    .than(
        CommandNode(DefinedString("release")).on_execution(
            lambda env, data: mcpython.common.DataPacks.datapack_handler.cleanup()
        )
    )
)
