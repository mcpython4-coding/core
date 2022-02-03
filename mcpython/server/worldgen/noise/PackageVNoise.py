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

import vnoise
from mcpython.server.worldgen.noise.INoiseImplementation import INoiseImplementation


def create_getter(n: vnoise.Noise):
    return lambda p: n.noise3(*p, *(0,) * (3 - len(p))) if len(p) < 4 else n.noise3(*p[:2], n.noise3(*p[2:], 10000))


class VNoiseImplementation(INoiseImplementation):
    """
    Noise implementation using the noise library
    todo: can we optional use numpy for some faster calcs
    """

    NAME = "minecraft:package_vnoise_noise"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noises: typing.List[typing.Optional[vnoise.Noise]] = [
            vnoise.Noise() for _ in range(self.octaves)
        ]

    def set_seed(self, seed: int):
        super().set_seed(seed)
        for i in range(self.octaves):
            self.noises[i].seed(hash((seed, i)))

    def calculate_position(self, position) -> float:
        assert len(position) == self.dimensions, "dimensions must match"
        position = tuple([e / self.scale for e in position])
        return self.merger.pre_merge(
            self,
            position,
            *[
                # todo: using two merged noises is not optimal...
                create_getter(n)
                for n in self.noises
            ]
        )
