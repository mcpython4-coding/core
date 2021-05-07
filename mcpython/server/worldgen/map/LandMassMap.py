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
class LandMassMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:landmass_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.land_mass_map: typing.Dict[typing.Tuple[int, int], str] = {}

    def load_from_saves(self, data):
        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16

        previous_mass = None

        for dx in range(16):
            for dz in range(16):
                index = data[0].pop(0)
                if index != -1:
                    previous_mass = data[1][index]

                self.set_at_xz(cx + dx, cz + dz, previous_mass)

    def dump_for_saves(self):
        cx, cz = self.chunk.get_position()
        cx *= 16
        cz *= 16
        data = [], []

        previous_mass = None
        for dx in range(16):
            for dz in range(16):
                mass = self.get_at_xz(cx + dx, cz + dz)
                if previous_mass == mass:
                    data[0].append(-1)
                elif mass in data[1]:
                    data[0].append(data[1].index(mass))
                else:
                    data[1].append(mass)
                    data[0].append(len(data[1]) - 1)

        return data

    def get_at_xz(self, x: int, z: int) -> str:
        return self.land_mass_map[x, z] if (x, z) in self.land_mass_map else "void"

    def set_at_xz(self, x: int, z: int, mass: str):
        self.land_mass_map[x, z] = mass

    def dump_debug_info(self, file: str):
        mass2color = {}
        image = PIL.Image.new("RGBA", (16, 16))
        for (x, z), mass in self.biome_map.items():
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
