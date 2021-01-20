import noise
from mcpython.server.worldgen.noise.INoiseImplementation import INoiseImplementation
import typing


class NoiseImplementation(INoiseImplementation):
    """
    Default noise implementation.
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
