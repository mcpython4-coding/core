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
import mcpython.server.worldgen.map.AbstractChunkInfoMap
import typing
from mcpython import shared
import PIL.Image
import random


@shared.world_generation_handler
class BiomeMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:biome_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.biome_map: typing.Dict[
            typing.Tuple[int, int, int], typing.Optional[str]
        ] = {}

    def load_from_saves(self, data):
        x, z = self.chunk.get_position()
        sx, sz = x * 16, z * 16
        for dx in range(0, 16, 4):
            for dz in range(0, 16, 4):
                previous_column = None

                for y in range(0, 256, 4):
                    index = data[0].pop(0)
                    if index != -1:
                        previous_column = data[1][index]

                    self.set_at_xyz(sx + x, y, sz + z, previous_column)

    def dump_for_saves(self):
        x, z = self.chunk.get_position()
        sx, sz = x * 16, z * 16
        data = ([], [])

        for dx in range(0, 16, 4):
            for dz in range(0, 16, 4):
                previous_column = None
                for y in range(0, 256, 4):
                    biome = self.get_at_xyz(sx + dx, y, sz + dz)
                    if biome != previous_column:
                        previous_column = biome
                        if biome in data[1]:
                            data[0].append(data[1].index(biome))
                        else:
                            data[1].append(biome)
                            data[0].append(len(data[1]) - 1)
                    else:
                        data[0].append(-1)

        return data

    def get_at_xz(self, x: int, z: int) -> str:
        return self.biome_map.setdefault((x // 4, 0, z // 4), None)

    def get_at_xyz(self, x: int, y: int, z: int) -> str:
        return self.biome_map.setdefault((x // 4, y // 4, z // 4), None)

    def set_at_xz(self, x: int, z: int, biome: str):
        for y in range(0, 256, 4):
            self.biome_map[x // 4, y, z // 4] = biome

    def set_at_xyz(self, x: int, y: int, z: int, biome: str):
        self.biome_map[x // 4, y // 4, z // 4] = biome

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
