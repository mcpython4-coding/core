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


class TemperatureMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:temperature_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.temperature_map: typing.Dict[typing.Tuple[int, int], float] = {}

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        for x, z in itertools.product(range(16), range(16)):
            buffer.write_float(self.get_at_xz(cx+x, cz+z))

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        for x, z in itertools.product(range(16), range(16)):
            self.set_at_xz(x+cx, z+cz, buffer.read_float())

    def get_at_xz(self, x: int, z: int) -> float:
        return self.temperature_map[x, z] if (x, z) in self.temperature_map else 0

    def set_at_xz(self, x: int, z: int, temperature: float):
        self.temperature_map[x, z] = temperature

    def dump_debug_info(self, file: str):
        image = PIL.Image.new("RGBA", (16, 16))
        for (x, z), temp in self.temperature_map.items():
            image.putpixel((x % 16, z % 16), temp * 255 % 256)
        image.save(file)


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(TemperatureMap)
