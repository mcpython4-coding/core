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
import importlib

from mcpython import logger
from mcpython.server.worldgen.noise.INoiseImplementation import (
    INoiseImplementation,
    IOctaveMerger,
    EQUAL_MERGER,
)


class NoiseImplementationWrapper(INoiseImplementation):
    def __init__(
        self,
        dimensions: int,
        octaves: int,
        scale: float,
        merger: IOctaveMerger = EQUAL_MERGER,
    ):
        super().__init__(dimensions, octaves, scale, merger)
        self.instance: typing.Optional[INoiseImplementation] = None

    def create_instance(self, cls: typing.Type[INoiseImplementation]):
        self.instance = cls(self.dimensions, self.octaves, self.scale, self.merger)
        self.instance.set_seed(self.seed)

    def set_seed(self, seed: int):
        super().set_seed(seed)
        if self.instance is not None:
            self.instance.set_seed(seed)

    def calculate_position(self, position) -> float:
        assert len(position) == self.dimensions, "dimensions must match"
        return self.instance.calculate_position(position)

    def calculate_area(
        self, start: typing.Tuple, end: typing.Tuple
    ) -> typing.Iterator[typing.Tuple[typing.Tuple, float]]:
        return self.instance.calculate_area(start, end)


class NoiseManager:
    def __init__(self):
        self.instances: typing.Dict[str, typing.Type[INoiseImplementation]] = {}
        self.default_implementation: typing.Optional[str] = None
        self.noise_instances: typing.List[
            typing.Tuple[NoiseImplementationWrapper, str]
        ] = []
        self.seed = 0

    def register_implementation(
        self, implementation: typing.Type[INoiseImplementation]
    ):
        if self.default_implementation is None:
            self.default_implementation = implementation.NAME
        self.instances[implementation.NAME] = implementation

    def set_noise_implementation(self, name: str = None):
        implementation = self.instances[
            name if name is not None else self.default_implementation
        ]
        for instance, _ in self.noise_instances:
            instance.create_instance(implementation)

    def register_optional_implementation(self, package: str, cls_name: str):
        try:
            self.register_implementation(
                getattr(importlib.import_module(package), cls_name)
            )
        except ImportError:
            logger.println(
                "[INFO] skipping noise implementation in {}".format(cls_name)
            )

    def create_noise_instance(
        self,
        ref_name: str,
        dimensions: int,
        octaves: int = 1,
        scale=1,
        merger: IOctaveMerger = EQUAL_MERGER,
    ) -> INoiseImplementation:
        instance = NoiseImplementationWrapper(dimensions, octaves, scale, merger=merger)
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
        if data is None:
            logger.println("[WARN] seed map is empty, skipping deserialization; This indicates a fatal error")
            return

        for noise, name in self.noise_instances:
            if name in data:
                noise.set_seed(data[name])
                del data[name]

        if "minecraft:noise_implementation" in data:
            self.set_noise_implementation(data["minecraft:noise_implementation"])

        if len(data) > 0:
            logger.println("found to many seed entries: ", data)


manager = NoiseManager()
from .OpenSimplexImplementation import OpenSimplexImplementation

manager.register_implementation(OpenSimplexImplementation)
manager.register_optional_implementation(
    "mcpython.server.worldgen.noise.PackageNoiseImplementation", "NoiseImplementation"
)
