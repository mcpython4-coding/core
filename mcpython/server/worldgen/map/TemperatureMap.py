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

import mcpython.server.worldgen.map.AbstractChunkInfoMap
import PIL.Image
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class TemperatureMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:temperature_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.temperature_data = array.ArrayType("f", (0,) * 256)

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)
        for e in self.temperature_data:
            buffer.write_float(e)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        self.temperature_data[:] = array.ArrayType("f", [buffer.read_float() for _ in range(256)])

    def get_at_xz(self, x: int, z: int) -> float:
        return self.temperature_data[x % 16 + z % 16 * 16]

    def set_at_xz(self, x: int, z: int, temperature: float):
        self.temperature_data[x % 16 + z % 16 * 16] = temperature

    def dump_debug_info(self, file: str):
        image = PIL.Image.new("RGBA", (16, 16))

        for x, z in itertools.product(range(16), repeat=2):
            temp = self.get_at_xz(x, z)
            image.putpixel((x % 16, z % 16), temp * 255 % 256)

        image.save(file)


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(TemperatureMap)
