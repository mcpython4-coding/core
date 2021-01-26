"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import noise
from mcpython.server.worldgen.noise.INoiseImplementation import INoiseImplementation
import typing


class NoiseImplementation(INoiseImplementation):
    """
    Noise implementation using the noise library
    """

    NAME = "minecraft:package_noise_noise"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noises: typing.List[typing.Optional[int]] = [None] * self.octaves

    def set_seed(self, seed: int):
        super().set_seed(seed)
        for i in range(self.octaves):
            self.noises[i] = hash((seed, i))

    def calculate_position(self, position) -> float:
        assert len(position) == self.dimensions, "dimensions must match"
        position = tuple([e / self.scale for e in position])
        return self.merger.pre_merge(
            self,
            position,
            *[
                # todo: using two merged noises is not optimal...
                lambda p: noise.snoise2(noise.snoise4(*p, *(0,) * (4 - len(p))), n)
                * 0.5
                + 0.5
                for n in self.noises
            ]
        )
