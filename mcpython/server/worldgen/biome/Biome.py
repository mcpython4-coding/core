"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.event.Registry
import mcpython.server.worldgen.feature.IOre
import mcpython.server.worldgen.feature.IFeature
import mcpython.common.world.AbstractInterface


class Biome(mcpython.common.event.Registry.IRegistryContent):
    NAME = "minecraft:unknown_biome"

    # name -> weight, group size
    PASSIVE_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {}
    HOSTILE_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {}
    AMBIENT_SPAWNS: typing.Dict[
        str, typing.Tuple[int, typing.Union[int, typing.Tuple[int, int]]]
    ] = {}

    GRASS_COLOR: typing.Optional[
        typing.Union[
            typing.Tuple[int, int, int],
            typing.Callable[[], typing.Tuple[int, int, int]],
        ]
    ] = None
    WATER_COLOR: typing.Optional[
        typing.Union[
            typing.Tuple[int, int, int],
            typing.Callable[[], typing.Tuple[int, int, int]],
        ]
    ] = None

    FEATURES = []
    FEATURES_SORTED = None

    @staticmethod
    def get_landmass() -> str:
        return "land"

    @staticmethod
    def get_weight() -> int:
        return 10

    @staticmethod
    def get_height_range() -> typing.Tuple[int, int]:
        return 10, 30

    @staticmethod
    def get_top_layer_height_range(
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.Tuple[int, int]:
        return 3, 5

    @staticmethod
    def get_top_layer_configuration(
        height: int,
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.List[str]:
        return ["minecraft:dirt"] * (height - 1) + ["minecraft:grass_block"]

    @staticmethod
    def get_trees() -> typing.List[
        typing.Tuple[mcpython.server.worldgen.feature.IFeature.IFeature, float]
    ]:
        return []

    @staticmethod
    def get_ores() -> typing.List[mcpython.server.worldgen.feature.IOre.IOre]:
        return []
