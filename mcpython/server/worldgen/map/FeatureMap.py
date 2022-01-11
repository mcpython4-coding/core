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
import array
import itertools
import typing

import mcpython.server.worldgen.map.AbstractChunkInfoMap
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class FeatureMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:feature_map"

    VERSION = 1

    def __init__(self, chunk):
        super().__init__(chunk)
        self.feature_map = array.ArrayType("B", (0,) * (16 * 16 * 256))
        self.feature_data = []

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        for _ in range(buffer.read_uint()):
            self.reserve_region(
                (buffer.read_long(), buffer.read_long(), buffer.read_long()),
                (buffer.read_long(), buffer.read_long(), buffer.read_long()),
                buffer.read_string(),
            )

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        buffer.write_uint(len(self.feature_data))

        for start, end, name in self.feature_data:
            buffer.write_long(start[0])
            buffer.write_long(start[1])
            buffer.write_long(start[2])
            buffer.write_long(end[0])
            buffer.write_long(end[1])
            buffer.write_long(end[2])
            buffer.write_string(name)

    def reserve_region(
        self,
        start: typing.Tuple[int, int, int],
        end: typing.Tuple[int, int, int],
        name: str,
    ):
        for x, y, z in itertools.product(
            *(range(start[i], end[i] + 1) for i in range(3))
        ):
            if x // 16 == self.chunk.position[0] and z // 16 == self.chunk.position[1]:
                self.feature_map[x % 16 + z % 16 * 16 + y * 256] += 1

        self.feature_data.append((start, end, name))

    def overlaps_with_region(
        self, start: typing.Tuple[int, int, int], end: typing.Tuple[int, int, int]
    ) -> bool:
        for x, y, z in itertools.product(
            *(range(start[i], end[i] + 1) for i in range(3))
        ):
            if x // 16 == self.chunk.position[0] and z // 16 == self.chunk.position[1]:
                if self.feature_map[x % 16 + z % 16 * 16 + y * 256] > 0:
                    return True
        return False


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(FeatureMap)
