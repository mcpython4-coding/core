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
from mcpython.server.command.Builder import Command, CommandNode, Int, DefinedString
from mcpython import shared
import mcpython.util.math
import itertools
from mcpython import logger


generate = (
    Command("generate")
    .info("generates the chunk standing in")
    .on_execution(
        lambda env, data: shared.world_generation_handler.generate_chunk(
            env.get_dimension().get_chunk(
                mcpython.util.math.position_to_chunk(env.get_position())
            )
        )
    )
    .than(
        CommandNode(Int())
        .of_name("X")
        .than(
            CommandNode(Int())
            .of_name("Z")
            .info("generates the given chunk")
            .on_execution(
                lambda env, data: shared.world_generation_handler.generate_chunk(
                    env.get_dimension().get_chunk(data[1], data[2])
                )
            )
        )
    )
    .than(
        CommandNode(DefinedString("area"))
        .of_name("area")
        .than(
            CommandNode(Int())
            .of_name("start X")
            .than(
                CommandNode(Int())
                .of_name("start Z")
                .than(
                    CommandNode(Int())
                    .of_name("end X")
                    .than(
                        CommandNode(Int())
                        .of_name("end Z")
                        .info("generates the given area")
                        .on_execution(
                            lambda env, data: [
                                logger.println(f"generating chunk {x} {z}")
                                # == for executing both sides in all cases
                                == shared.world_generation_handler.generate_chunk(
                                    env.get_dimension().get_chunk(x, z)
                                )
                                for x, z in itertools.product(
                                    range(data[2], data[4] + 1),
                                    range(data[3], data[5] + 1),
                                )
                            ]
                        )
                    )
                )
            )
        )
    )
)
