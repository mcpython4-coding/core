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
import PIL.Image
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class BiomeMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:biome_map"

    VERSION = 2

    def __init__(self, chunk):
        super().__init__(chunk)

        self.biome_data = array.ArrayType("b", (0,) * (4 * 4 * 16))
        self.reference_table = [None]

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        data = [buffer.read_uint() for _ in range(4 * 4 * 16)]
        self.biome_data[:] = array.ArrayType("b", data)

        biomes = await buffer.collect_list(lambda: buffer.read_string(size_size=1))
        self.reference_table = [None] + biomes

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        for p in self.biome_data:
            buffer.write_uint(p)

        await buffer.write_list(self.reference_table[1:], lambda e: buffer.write_string(e, size_size=1))

    def get_at_xyz(self, x: int, y: int, z: int) -> str | None:
        return self.reference_table[self.biome_data[x // 4 % 4 + z // 4 % 4 * 4 + y // 4 % 4 * 16]]

    def set_at_xyz(self, x: int, y: int, z: int, biome: str | None):
        if biome in self.reference_table:
            index = self.reference_table.index(biome)
        else:
            index = len(self.reference_table)
            self.reference_table.append(biome)

        self.biome_data[x // 4 % 4 + z // 4 % 4 * 4 + y * 16] = index

    def dump_debug_info(self, file: str):
        biome2color = {}
        image = PIL.Image.new("RGBA", (16, 16))
        cx, cz = self.chunk
        for x, z in itertools.product(range(cx*16, cx*16+16, 4), range(cz*16, cz*16+16, 4)):
            biome = self.get_at_xz(x, z)

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

    def get_biome_color_at(self, x: int, y: int, z: int) -> typing.Tuple[float, float, float]:
        # todo: implement biome color blending
        biome = self.get_at_xyz(x, y, z)
        return tuple(e / 256 for e in shared.biome_handler.biomes[biome].GRASS_COLOR) if biome is not None else (91 / 255, 201 / 255, 59 / 255)


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(BiomeMap)
