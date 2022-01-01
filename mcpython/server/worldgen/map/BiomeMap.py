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
import random
import typing

import mcpython.server.worldgen.map.AbstractChunkInfoMap
import PIL.Image
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer
from mcpython.engine.network.util import WriteBuffer


class BiomeMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:biome_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.biome_map: typing.Dict[
            typing.Tuple[int, int, int], typing.Optional[str]
        ] = {}

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        x, z = self.chunk.get_position()
        sx, sz = x * 16, z * 16

        data = iter([buffer.read_uint() for _ in range(16*16)])

        biomes = await buffer.collect_list(lambda: buffer.read_string(size_size=1))

        for x, z in itertools.product(range(16), range(16)):
            index = next(data)
            self.set_at_xz(x+sx, z+sz, biomes[index-1] if index != 0 else None)

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        x, z = self.chunk.get_position()
        sx, sz = x * 16, z * 16
        table = []

        for x, z in itertools.product(range(16), range(16)):
            biome = self.get_at_xz(x+sx, z+sz)

            if biome is None:
                buffer.write_uint(0)
            else:
                if biome not in table:
                    table.append(biome)
                    buffer.write_uint(len(table))
                else:
                    buffer.write_uint(table.index(biome)+1)

        await buffer.write_list(table, lambda e: buffer.write_string(e, size_size=1))

    def get_at_xz(self, x: int, z: int) -> str | None:
        return self.biome_map.setdefault((x, 0, z), None)

    def get_at_xyz(self, x: int, y: int, z: int) -> str | None:
        return self.biome_map.setdefault((x, y, z), None)

    def set_at_xz(self, x: int, z: int, biome: str | None):
        for y in range(0, 256):
            self.biome_map[x, y, z] = biome

    def set_at_xyz(self, x: int, y: int, z: int, biome: str | None):
        self.biome_map[x, y, z] = biome

    def dump_debug_info(self, file: str):
        biome2color = {}
        image = PIL.Image.new("RGBA", (16, 16))
        for (x, y, z), biome in self.biome_map.items():
            if biome not in biome2color:
                seed = hash(biome)
                biome2color[biome] = (
                    seed % 256,
                    seed % (256 ** 2) // 256,
                    seed % (256 ** 3) // (256 ** 2),
                    255,
                )
            image.putpixel((x % 16, z % 16), biome2color[biome])
        image.save(file)


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(BiomeMap)
