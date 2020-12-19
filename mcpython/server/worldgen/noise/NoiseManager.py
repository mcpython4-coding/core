"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import itertools
import typing
import opensimplex


class INoiseImplementation:
    NAME = None

    def __init__(self, dimensions: int, octaves: int, scale: float):
        self.seed = 0
        self.dimensions = dimensions
        self.octaves = octaves
        self.scale = scale

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
    NAME = "minecraft:open_simplex"

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
        values = []
        if self.dimensions == 2:
            for noise in self.noises:
                values.append(noise.noise2d(*position))
        elif self.dimensions == 3:
            for noise in self.noises:
                values.append(noise.noise3d(*position))
        elif self.dimensions == 4:
            for noise in self.noises:
                values.append(noise.noise4d(*position))
        elif self.dimensions == 1:
            for noise in self.noises:
                values.append(noise.noise2d(0, *position))
        else:
            raise NotImplementedError("unable to calculate noise map!")
        return (sum(values) / len(values) + 1) / 2


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
    ) -> INoiseImplementation:
        if implementation is None:
            implementation = self.default_implementation
        instance = self.instances[implementation](dimensions, octaves, scale)
        instance.set_seed(self.calculate_part_seed(ref_name))
        self.noise_instances.append((instance, ref_name))
        return instance

    def recalculate_noises(self):
        for instance, name in self.noise_instances:
            instance.set_seed(self.calculate_part_seed(name))

    def calculate_part_seed(self, part: str):
        return hash((hash(part), self.seed))


manager = NoiseManager()
manager.register_implementation(OpenSimplexImplementation)
