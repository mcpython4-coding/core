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
import typing

import mcpython.server.worldgen.map.AbstractChunkInfoMap
import PIL.Image
from mcpython import shared


@shared.world_generation_handler
class TemperatureMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:temperature_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.temperature_map: typing.Dict[typing.Tuple[int, int], float] = {}

    def load_from_saves(self, data):
        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        for dx in range(16):
            for dz in range(16):
                self.set_at_xz(cx + dx, cz + dz, data.pop(0))

    def dump_for_saves(self):
        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16
        data = []

        for dx in range(16):
            for dz in range(16):
                data.append(self.get_at_xz(cx + dx, cz + dz))

        return data

    def get_at_xz(self, x: int, z: int) -> float:
        return self.temperature_map[x, z] if (x, z) in self.temperature_map else 0

    def set_at_xz(self, x: int, z: int, temperature: float):
        self.temperature_map[x, z] = temperature

    def dump_debug_info(self, file: str):
        image = PIL.Image.new("RGBA", (16, 16))
        for (x, z), temp in self.biome_map.items():
            image.putpixel((x % 16, z % 16), temp * 255 % 256)
        image.save(file)
