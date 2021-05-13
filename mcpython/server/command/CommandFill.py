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
import mcpython.common.world.util
from mcpython.server.command.Builder import (Block, Command, CommandNode,
                                             DefinedString, IntPosition)


def default_fill(dim, start, end, block_source):
    mcpython.common.world.util.fill_area_replacing(
        dim,
        start,
        end,
        block_source,
        mcpython.common.world.util.AnyBlock([block_source]),
    )


fill = Command("fill").than(
    CommandNode(IntPosition())
    .of_name("start")
    .than(
        CommandNode(IntPosition())
        .of_name("end")
        .than(
            CommandNode(Block())
            .of_name("block")
            .info("fills the given region with the given block")
            .on_execution(
                lambda env, data: default_fill(env.get_dimension(), *data[1:4])
            )
            .than(
                CommandNode(DefinedString("replace"))
                .of_name("replace")
                .info("replaces all blocks")
                .on_execution(
                    lambda env, data: default_fill(env.get_dimension(), *data[1:4])
                )
                .than(
                    CommandNode(Block())
                    .of_name("replacing")
                    .info("replaces all blocks of the given type with the given block")
                    .on_execution(
                        lambda env, data: mcpython.common.world.util.fill_area_replacing(
                            env.get_dimension(), data[1], data[2], data[3], data[5]
                        )
                    )
                )
            )
            .than(
                CommandNode(DefinedString("destroy"))
                .of_name("destroy")
                .info("replaces all blocks, including identical blocks")
                .on_execution(
                    lambda env, data: mcpython.common.world.util.fill_area(
                        env.get_dimension(), data[1], data[2], data[3]
                    )
                )
            )
            .than(
                CommandNode(DefinedString("keep"))
                .of_name("keep")
                .info("replaces only air")
                .on_execution(
                    lambda env, data: mcpython.common.world.util.fill_area_replacing(
                        env.get_dimension(), data[1], data[2], data[3], "minecraft:air"
                    )
                )
            )
            .than(
                CommandNode(DefinedString("hollow"))
                .of_name("hollow")
                .info("creates a hollow structure with air in the middle")
                .on_execution(
                    lambda env, data: mcpython.common.world.util.create_hollow_structure(
                        env.get_dimension(), data[1], data[2], data[3], fill_center=True
                    )
                )
            )
            .than(
                CommandNode(DefinedString("outline"))
                .of_name("outline")
                .info("creates a hollow structure without replacing the core")
                .on_execution(
                    lambda env, data: mcpython.common.world.util.create_hollow_structure(
                        env.get_dimension(), data[1], data[2], data[3]
                    )
                )
            )
        )
    )
)
