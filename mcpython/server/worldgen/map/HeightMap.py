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

    def get_at_xz(self, x: int, z: int):
        return self.height_map[x, z] if (x, z) in self else [(0, 0)]

    def set_at_xz(self, x: int, z: int, height):
        self.height_map[x, z] = height

    def __contains__(self, item):
        return item in self.height_map
