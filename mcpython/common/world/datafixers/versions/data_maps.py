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

from mcpython.server.worldgen.map.AbstractChunkInfoMap import AbstractMap
from mcpython.common.block.Furnace import Smoker
from mcpython.common.world.datafixers.NetworkFixers import ChunkInfoMapFixer
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer
from mcpython.server.worldgen.map.BiomeMap import BiomeMap


class BiomeMap_0_1Fixer(ChunkInfoMapFixer):
    """
    Fixes the migration of the "progress" attribute and others of the Furnace block from int to float
    Below are the two classes for the blast furnace and smoker blocks, as they are delivered from the
    furnace block
    """

    MAP_NAME = "minecraft:biome_map"

    BEFORE_VERSION: int = 0
    AFTER_VERSION: int = 1

    @classmethod
    async def apply2stream(cls, target: BiomeMap, source_buffer: ReadBuffer, target_buffer: WriteBuffer):
        x, z = target.chunk.get_position()
        sx, sz = x * 16, z * 16

        data = iter([source_buffer.read_uint() for _ in range(16 * 16)])

        biome_list = await source_buffer.collect_list(lambda: source_buffer.read_string(size_size=1))

        biomes = {}

        for x, z in itertools.product(range(16), range(16)):
            index = next(data)
            biomes[x + sx, z + sz] = biome_list[index - 1] if index != 0 else None

        table = []

        for x, z in itertools.product(range(0, 16, 4), range(0, 16, 4)):
            biome = biomes[x + sx, z + sz]

            if biome is None:
                target_buffer.write_uint(0)
            else:
                if biome not in table:
                    table.append(biome)
                    target_buffer.write_uint(len(table))
                else:
                    target_buffer.write_uint(table.index(biome) + 1)

        await target_buffer.write_list(table, lambda e: target_buffer.write_string(e, size_size=1))
