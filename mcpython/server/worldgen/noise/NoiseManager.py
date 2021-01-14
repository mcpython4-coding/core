"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import itertools
import typing
import opensimplex
import mcpython.util.math

from mcpython import logger


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
        for position in itertools.product(*(range(a, b) for a, b in zip(start, end))):
            yield position, self.calculate_position(position)


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
                lambda p: noise.noise4d(*p, *(0,) * (4 - len(p))) * 0.5 + 0.5
                for noise in self.noises
            ]
        )


class NoiseManager:
    def __init__(self):
        self.instances: typing.Dict[str, typing.Type[INoiseImplementation]] = {}
        self.default_implementation: typing.Optional[str] = None
        self.noise_instances: typing.List[typing.Tuple[INoiseImplementation, str]] = []
        self.seed = 0

    def register_implementation(
        self, implementation: typing.Type[INoiseImplementation]
    ):
        if self.default_implementation is None:
            self.default_implementation = implementation.NAME
        self.instances[implementation.NAME] = implementation

    def create_noise_instance(
        self,
        ref_name: str,
        dimensions: int,
        octaves: int = 1,
        implementation=None,
        scale=1,
        merger: IOctaveMerger = EQUAL_MERGER,
    ) -> INoiseImplementation:
        if implementation is None:
            implementation = self.default_implementation
        instance = self.instances[implementation](
            dimensions, octaves, scale, merger=merger
        )
        instance.set_seed(self.calculate_part_seed(ref_name))
        self.noise_instances.append((instance, ref_name))
        return instance

    def recalculate_noises(self):
        for instance, name in self.noise_instances:
            instance.set_seed(self.calculate_part_seed(name))

    def calculate_part_seed(self, part: str):
        return hash((hash(part), self.seed))

    def serialize_seed_map(self) -> dict:
        return {name: noise.seed for (noise, name) in self.noise_instances}

    def deserialize_seed_map(self, data: dict):
        for noise, name in self.noise_instances:
            if name in data:
                noise.set_seed(data[name])
                del data[name]
        if len(data) > 0:
            logger.println("found to many seed entries: ", data)


manager = NoiseManager()
manager.register_implementation(OpenSimplexImplementation)
