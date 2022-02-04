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
import struct

from mcpython.common.world.datafixers.NetworkFixers import ChunkInfoMapFixer
from mcpython.engine import logger
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython.server.worldgen.map.BiomeMap import BiomeMap


class BiomeMap_0_1Fixer(ChunkInfoMapFixer):
    MAP_NAME = "minecraft:biome_map"

    BEFORE_VERSION: int = 0
    AFTER_VERSION: int = 1

    @classmethod
    async def apply2stream(
        cls, target: BiomeMap, source_buffer: ReadBuffer, target_buffer: WriteBuffer
    ):
        try:
            data = iter([source_buffer.read_uint() for _ in range(16 * 16)])
            biome_list = await source_buffer.collect_list(
                lambda: source_buffer.read_string(size_size=1)
            )

        except struct.error:
            logger.print_exception("During data fixing")
            data = (0 for _ in range(16 * 16))
            biome_list = []

        biomes = {}

        for x, z in itertools.product(range(16), range(16)):
            index = next(data)
            biomes[x, z] = biome_list[index - 1] if index != 0 else None

        table = []

        for x, z in itertools.product(range(0, 16, 4), range(0, 16, 4)):
            biome = biomes[x, z]

            if biome is None:
                target_buffer.write_uint(0)
            else:
                if biome not in table:
                    table.append(biome)
                    target_buffer.write_uint(len(table))
                else:
                    target_buffer.write_uint(table.index(biome) + 1)

        await target_buffer.write_list(
            table, lambda e: target_buffer.write_string(e, size_size=1)
        )


class BiomeMap_1_2Fixer(ChunkInfoMapFixer):
    MAP_NAME = "minecraft:biome_map"

    BEFORE_VERSION: int = 1
    AFTER_VERSION: int = 2

    @classmethod
    async def apply2stream(
        cls, target: BiomeMap, source_buffer: ReadBuffer, target_buffer: WriteBuffer
    ):
        data = source_buffer.read_const_bytes(4 * 4 * 4)
        biomes = await source_buffer.collect_list(
            lambda: source_buffer.read_string(size_size=1)
        )

        for _ in range(16):
            target_buffer.write_const_bytes(data)

        await target_buffer.write_list(
            biomes, lambda e: target_buffer.write_string(e, size_size=1)
        )
