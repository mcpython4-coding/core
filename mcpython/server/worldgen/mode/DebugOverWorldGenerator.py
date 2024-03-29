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
import math

import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython
import mcpython.engine.event.EventHandler
import mcpython.server.worldgen.mode.IWorldGenConfig
import mcpython.server.worldgen.WorldGenerationTaskArrays
import mcpython.util.math
from mcpython import shared


class BlockInfo:
    TABLE = {}  # {chunk: tuple<x, z> -> {position<x,z> -> blockname}}

    @classmethod
    async def construct(cls):
        BLOCKS: mcpython.common.event.Registry.Registry = shared.registry.get_by_name(
            "minecraft:block"
        )

        block_table = list(BLOCKS.entries.values())
        block_table.sort(key=lambda x: x.NAME)
        blocklist = []
        for block in block_table:
            for state in block.DEBUG_WORLD_BLOCK_STATES:
                blocklist.append((block, state))

        size = math.ceil(len(blocklist) ** 0.5)
        hsize = size // 2 + 1

        rx, ry = -hsize, -hsize

        for block, state in blocklist:
            x, y = rx * 4, ry * 4
            chunk = mcpython.util.math.position_to_chunk((x, 0, y))
            cls.TABLE.setdefault(chunk, {})[(x, y)] = (block.NAME, state)
            rx += 1
            if x >= hsize:
                ry += 1
                rx = -hsize


class DebugWorldGenerator(
    mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig
):
    NAME = "minecraft:debug_world_generator"
    DIMENSION = "minecraft:overworld"
    DISPLAY_NAME = "DEBUG GENERATOR"

    @classmethod
    def on_chunk_prepare_generation(
        cls,
        chunk,
        array: mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference,
    ):
        cx, cz = chunk.position

        if (cx, cz) in BlockInfo.TABLE:
            height_map = chunk.get_map("minecraft:height_map")
            block_map = BlockInfo.TABLE[(cx, cz)]
            for x, z in block_map.keys():
                block, state = block_map[(x, z)]
                array.schedule_block_add(
                    (x, 10, z), block, block_update=False, block_state=state
                )
                height_map.set_at_xz(
                    x, z, [(0, 30)]
                )  # todo: relative to lower world limit

            for x in range(16):
                for z in range(16):
                    array.schedule_block_add(
                        (cx * 16 + x, 5, cz * 16 + z), "minecraft:barrier"
                    )

        if shared.world.get_active_player().gamemode != 3:
            shared.world.get_active_player().set_gamemode(3)
        shared.world.get_active_player().flying = True


shared.world_generation_handler.register_world_gen_config(DebugWorldGenerator)

mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:post", BlockInfo.construct(), info="constructing debug world info"
)
