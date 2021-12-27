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

import opensimplex
from mcpython.server.worldgen.noise.INoiseImplementation import INoiseImplementation


class OpenSimplexImplementation(INoiseImplementation):
    """
    Default noise implementation.
    """

    NAME = "minecraft:open_simplex_noise"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noises: typing.List[typing.Optional[opensimplex.OpenSimplex]] = [
            None
        ] * self.octaves

    def set_seed(self, seed: int):
        super().set_seed(seed)
        for i in range(self.octaves):
            self.noises[i] = opensimplex.OpenSimplex(hash((seed, i)))

    def calculate_position(self, position) -> float:
        assert len(position) == self.dimensions, "dimensions must match"
        position = tuple([e / self.scale for e in position])
        return self.merger.pre_merge(
            self,
            position,
            *[
                lambda p: noise.noise4(*p, *(0,) * (4 - len(p))) * 0.5 + 0.5
                for noise in self.noises
            ]
        )
