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
import enum
import random
from abc import ABC

import mcpython.engine.world.AbstractInterface
import mcpython.server.worldgen.feature.IFeature
from mcpython import shared


def place_default(
    x: int,
    y: int,
    z: int,
    sx: int,
    sy: int,
    sz: int,
    blocks: list,
    replace: list,
    dimension: mcpython.engine.world.AbstractInterface.IDimension,
):
    for dx in range(sx, sx + 1):
        for dy in range(sy, sy + 1):
            for dz in range(sz, sz + 1):
                if dx**2 / sx**2 + dy**2 / sy**2 + dz**2 / sz**2 <= 1:
                    rx, ry, rz = dx + x, dy + y, dz + z
                    block = dimension.get_block((rx, ry, rz))
                    name = block.NAME if block else None
                    if name in replace:
                        dimension.get_chunk_for_position(
                            (rx, ry, rz)
                        ).add_add_block_gen_task((rx, ry, rz), random.choice(blocks))


class OrePlacementMode(enum.Enum):
    DEFAULT = 0  # args: minh, maxh
    MIDDLE_HIGHEST = 1  # args: minh, maxh, minchance


class IOre(mcpython.server.worldgen.feature.IFeature.IFeature):
    @staticmethod
    def place(dimension, x, y, z, **config):
        pass

    @staticmethod
    def get_height_range() -> tuple:
        raise NotImplementedError()

    @staticmethod
    def get_ore_block() -> str or list:
        """
        :return: an ore-name or a list of ore-names or a {ore-name: chance} table
        """
        raise NotImplementedError()

    @staticmethod
    def get_replacement_blocks():
        return ["minecraft:stone"]

    @staticmethod
    def get_size_range() -> tuple:
        raise NotImplementedError()

    @staticmethod
    def get_chunk_count() -> int:
        raise NotImplementedError()

    @staticmethod
    def get_ore_height() -> int:
        raise NotImplementedError()


class INormalOre(IOre, ABC):
    @classmethod
    def place(cls, dimension, x, y, z, **config):
        size = round(random.randint(*cls.get_size_range()) ** (1 / 3))
        rx, ry, rz = (
            random.randint(1, size),
            random.randint(1, size),
            random.randint(1, size),
        )
        ores = cls.get_ore_block()
        if type(ores) == str:
            ores = [ores]
        place_default(
            x, y, z, rx, ry, rz, ores, cls.get_replacement_blocks(), dimension
        )

    @classmethod
    def get_ore_height(cls) -> int:
        return random.randint(*cls.get_height_range())


class CoalOre(INormalOre):
    @staticmethod
    def get_size_range() -> tuple:
        return 4, 17

    @staticmethod
    def get_chunk_count() -> int:
        return 20

    @staticmethod
    def get_height_range() -> tuple:
        return 0, 127

    @staticmethod
    def get_ore_block() -> str or list:
        return "minecraft:coal_ore"


@shared.registry
class DefaultOreFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:default_ore_feature"


@shared.registry
class DefaultEmeraldFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:default_emerald_ore_feature"


@shared.registry
class DefaultInfestedStoneFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:default_infested_stone_feature"
