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

import mcpython.util.math


class IOctaveMerger:
    @classmethod
    def pre_merge(
        cls,
        implementation: "INoiseImplementation",
        position,
        *generators: typing.Callable
    ) -> float:
        return cls.merge(
            implementation, [generator(position) for generator in generators]
        )

    @classmethod
    def merge(cls, implementation: "INoiseImplementation", values) -> float:
        return 0


class EQUAL_MERGER(IOctaveMerger):
    @classmethod
    def merge(cls, implementation: "INoiseImplementation", values):
        return sum(values) / len(values)


class WeightedEqualMerger(IOctaveMerger):
    def __init__(self, weights: typing.Iterable[float]):
        self.weights = weights

        s = sum(weights)
        self.normalized_weights = [e / s for e in weights]

    def merge(self, implementation: "INoiseImplementation", values):
        return sum(map(lambda e: e[0] * e[1], zip(values, self.normalized_weights)))


class GEO_EQUAL_MERGER(IOctaveMerger):
    @classmethod
    def merge(cls, implementation: "INoiseImplementation", values):
        return mcpython.util.math.product(values) ** (1 / len(values))


class INNER_MERGE(IOctaveMerger):
    @classmethod
    def pre_merge(
        cls,
        implementation: "INoiseImplementation",
        position,
        *generators: typing.Callable
    ):
        if implementation.merger_config is None:
            implementation.merger_config = [1] * len(generators)
        if len(implementation.merger_config) < len(generators):
            implementation.merger_config += [1] * (
                len(generators) - len(implementation.merger_config)
            )
        value = generators[0](position) * implementation.merger_config[0]
        for i, generator in enumerate(generators[1:]):
            value = generator(position + (value,)) * implementation.merger_config[i + 1]
        return value


class INoiseImplementation:
    NAME = None

    def __init__(
        self,
        dimensions: int,
        octaves: int,
        scale: float,
        merger: IOctaveMerger = EQUAL_MERGER,
    ):
        self.seed = 0
        self.dimensions = dimensions
        self.octaves = octaves
        self.scale = scale
        self.merger = merger
        self.merger_config = None

    def set_seed(self, seed: int):
        self.seed = seed

    def calculate_position(self, position) -> float:
        assert len(position) == self.dimensions, "dimensions must match"
        return 0

    def calculate_area(
        self, start: typing.Tuple, end: typing.Tuple
    ) -> typing.Iterator[typing.Tuple[typing.Tuple, float]]:
        for position in itertools.product(
            *(range(int(a), int(b)) for a, b in zip(start, end))
        ):
            yield position, self.calculate_position(position)
