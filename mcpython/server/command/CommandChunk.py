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
import itertools
import os

import mcpython.util.math
from mcpython import logger, shared
from mcpython.server.command.Builder import (Command, CommandNode,
                                             DefinedString, Int)

chunk = (
    Command("chunk")
    .than(
        CommandNode(DefinedString("generate"))
        .of_name("generate")
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
                                        range(data[3], data[5] + 1),
                                        range(data[4], data[6] + 1),
                                    )
                                ]
                            )
                        )
                    )
                )
            )
        )
    )
    .than(
        CommandNode(DefinedString("delete"))
        .of_name("delete")
        .info("deletes the content of the current chunk")
        .on_execution(lambda env, data: env.get_current_chunk().clear())
        .than(
            CommandNode(DefinedString("all"))
            .of_name("all")
            .info("deletes all chunks in the current dim")
            .on_execution(
                lambda env, data: [
                    c.clear() for c in env.get_dimension().chunk_iterator()
                ]
            )
        )
    )
    .than(
        CommandNode(DefinedString("save"))
        .of_name("save")
        .info("saves the current chunk")
        .on_execution(lambda env, data: env.get_current_chunk().save())
        .than(
            CommandNode(DefinedString("all"))
            .of_name("all")
            .info("saves all chunks in the current dimension")
            .on_execution(
                lambda env, data: [
                    c.save() for c in env.get_dimension().chunk_iterator()
                ]
            )
        )
    )
    .than(
        CommandNode(DefinedString("visualupdate"))
        .of_name("visual update")
        .info("updates the visible state of all blocks in that chunk")
        .on_execution(lambda env, data: env.get_current_chunk().update_all_rendering())
        .than(
            CommandNode(DefinedString("all"))
            .of_name("all")
            .info("visual-updates all chunks in the current dimension")
            .on_execution(
                lambda env, data: [
                    c.update_all_rendering()
                    for c in env.get_dimension().chunk_iterator()
                ]
            )
        )
    )
    .than(
        CommandNode(DefinedString("dumpdatadebug"))
        .of_name("dump data debug")
        .info("dumps the debug information")
        .on_execution(
            lambda env, data: os.makedirs(shared.home + "/debug_chunk_maps")
            == env.get_current_chunk().dump_debug_maps(
                shared.home + "/debug_chunk_maps/debug_map_{}.png"
            )
        )
        .than(
            CommandNode(DefinedString("all"))
            .of_name("all")
            .info("dumps all maps to files")
            .on_execution(
                lambda env, data: env.get_dimension().dump_debug_maps_all_chunks(
                    shared.home + "/debug_chunk_maps/{}.png"
                )
            )
        )
    )
)
