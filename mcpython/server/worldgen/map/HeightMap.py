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
import typing

import mcpython.server.worldgen.map.AbstractChunkInfoMap
import PIL.Image
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer
from mcpython.engine.network.util import WriteBuffer


class HeightMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    """
    Representation of a heightmap in-code
    Each chunk has one in the normal case

    Contains also the serializer code
    todo: implement better serializer
    """

    NAME = "minecraft:height_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.height_map: typing.Dict[
            typing.Tuple[int, int], typing.List[typing.Tuple[int, int]]
        ] = {}

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        async def write_part(data):
            await buffer.write_list(
                [e async for e in data] if not isinstance(data, list) else data,
                lambda e: buffer.write_int(e[0]).write_int(e[1]),
            )

        await buffer.write_list([
            self.get_at_xz(x+cx, z+cz)
            for x, z in itertools.product(range(16), range(16))
        ], write_part)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        async def read_part():
            return buffer.collect_list(lambda: (buffer.read_int(), buffer.read_int()))

        data = await buffer.collect_list(read_part)
        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        for x, z in itertools.product(range(16), range(16)):
            self.set_at_xz(x+cx, z+cz, data.pop(0))

    def get_at_xz(self, x: int, z: int) -> typing.List[typing.Tuple[int, int]]:
        return self.height_map[x, z] if (x, z) in self else [(0, 0)]

    def set_at_xz(self, x: int, z: int, height):
        self.height_map[x, z] = height

    def __contains__(self, item):
        return item in self.height_map


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(HeightMap)
