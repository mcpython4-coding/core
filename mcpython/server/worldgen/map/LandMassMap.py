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
        self.land_mass_map: typing.Dict[typing.Tuple[int, int], str] = {}

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16
        table = []

        for x, z in itertools.product(range(16), range(16)):
            mass = self.get_at_xz(x + cx, z + cz)

            if mass is None:
                buffer.write_byte(0)
            else:
                if mass not in table:
                    table.append(mass)
                    buffer.write_byte(len(table))
                else:
                    buffer.write_byte(table.index(mass) + 1)

        await buffer.write_list(table, lambda e: buffer.write_string(e, size_size=2))

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        data = iter([buffer.read_byte() for _ in range(16 * 16)])
        table = await buffer.collect_list(lambda: buffer.read_string(size_size=2))

        for x, z in itertools.product(range(16), range(16)):
            index = next(data)
            self.set_at_xz(x + cx, z + cz, table[index - 1] if index != 0 else None)

    def get_at_xz(self, x: int, z: int) -> str:
        return self.land_mass_map[x, z] if (x, z) in self.land_mass_map else "void"

    def set_at_xz(self, x: int, z: int, mass: str):
        self.land_mass_map[x, z] = mass

    def dump_debug_info(self, file: str):
        mass2color = {}
        image = PIL.Image.new("RGBA", (16, 16))
        for (x, z), mass in self.land_mass_map.items():
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
