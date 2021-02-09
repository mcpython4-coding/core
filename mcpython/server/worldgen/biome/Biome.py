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
from abc import ABC

import mcpython.common.event.Registry
import mcpython.server.worldgen.feature.IOre
import mcpython.server.worldgen.feature.IFeature
import mcpython.common.world.AbstractInterface


class Biome(mcpython.common.event.Registry.IRegistryContent, ABC):
    """
    Abstract base class for biomes
    Defines the look of the biome
    todo: add factory for it
    """

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

    CARVERS = []  # for the future...

    @classmethod
    def get_landmass(cls) -> str:
        return "land"

    @classmethod
    def get_weight(cls) -> int:
        return 10

    @classmethod
    def get_height_range(cls) -> typing.Tuple[int, int]:
        return 10, 30

    @classmethod
    def get_top_layer_height_range(
        cls,
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.Tuple[int, int]:
        return 3, 5

    @classmethod
    def get_top_layer_configuration(
        cls,
        height: int,
        position: typing.Tuple[int, int],
        dimension: mcpython.common.world.AbstractInterface.IDimension,
    ) -> typing.List[str]:
        return ["minecraft:dirt"] * (height - 1) + ["minecraft:grass_block"]
