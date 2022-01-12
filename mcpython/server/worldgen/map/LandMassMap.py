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
from mcpython.engine.world.AbstractInterface import IChunk


class LandMassMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    """
    Class storing which land mass we are in
    todo: migrate to biome map
    """

    NAME = "minecraft:landmass_map"

    def __init__(self, chunk: IChunk):
        super().__init__(chunk)

        self.land_mass_table = array.ArrayType("b", (0,) * (16 * 16))
        self.reference_table = ["void"]

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        assert len(self.land_mass_table) == 256

        for index in self.land_mass_table:
            buffer.write_byte(index)

        await buffer.write_list(self.reference_table[1:], lambda e: buffer.write_string(e, size_size=2))

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        self.land_mass_table[:] = array.ArrayType("b", [buffer.read_byte() for _ in range(16 * 16)])

        self.reference_table[:] = ["void"] + await buffer.collect_list(lambda: buffer.read_string(size_size=2))

    def get_at_xz(self, x: int, z: int) -> str:
        return self.reference_table[
            self.land_mass_table[x % 16 + z % 16 * 16]
        ]

    def set_at_xz(self, x: int, z: int, mass: str):
        if mass in self.reference_table:
            index = self.reference_table.index(mass)
        else:
            index = len(self.reference_table)
            self.reference_table.append(mass)

        self.land_mass_table[x % 16 + z % 16 * 16] = index

    def dump_debug_info(self, file: str):
        mass2color = {}
        image = PIL.Image.new("RGBA", (16, 16))
        for x, z in itertools.product(range(2), repeat=2):
            mass = self.get_at_xz(x, z)
            if mass not in mass2color:
                seed = hash(mass)
                mass2color[mass] = (
                    seed % 256,
                    seed % (256 ** 2) // 256,
                    seed % (256 ** 3) // (256 ** 2),
                    255,
                )
            image.putpixel((x % 16, z % 16), mass2color[mass])
        image.save(file)


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(LandMassMap)
