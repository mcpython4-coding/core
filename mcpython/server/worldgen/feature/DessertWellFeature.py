"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.worldgen.feature.IFeature
import mcpython.server.worldgen.WorldGenerationTaskArrays
import mcpython.util.enums
from mcpython import shared


@shared.registry
class DessertWellFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:dessert_well_feature"

    SAND_LIKE = [
        "minecraft:sand",
        "minecraft:red_sand",
        "minecraft:sandstone",
        "minecraft:red_sandstone",
    ]
    SANDSTONE = "minecraft:sandstone"
    SANDSTONE_SLAB = "minecraft:sandstone_slab"
    WATER = None

    @classmethod
    def place_array(
        cls,
        array: mcpython.server.worldgen.WorldGenerationTaskArrays.IWorldGenerationTaskHandlerReference,
        x: int,
        y: int,
        z: int,
        config,
    ):
        """
        Code ported from minecraft using minecraft forge dev-environment for version 1.16.4
        """

        while array.get_block((x, y, z)) is None and y > 2:
            y -= 1

        if array.get_block_name((x, y, z)) not in cls.SAND_LIKE:
            return

        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if (
                    array.get_block((x + dx, -1, z + dz)) is None
                    and array.get_block((x + dx, -2, z + dz)) is None
                ):
                    return

        for dy in range(-1, 1):
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    array.schedule_block_add((x + dx, y + dy, z + dz), cls.SANDSTONE)

        array.schedule_block_add((x, y, z), cls.WATER)

        for dx, dy, dz in mcpython.util.enums.HORIZONTAL_OFFSETS:
            array.schedule_block_add((x + dx, y + dy, z + dz), cls.WATER)

        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx == -2 or dx == 2 or dz == -2 or dz == 2:
                    array.schedule_block_add((x + dx, y + 1, z + dz), cls.SANDSTONE)

        array.schedule_block_add((x + 2, y + 1, 0), cls.SANDSTONE_SLAB)
        array.schedule_block_add((x - 2, y + 1, 0), cls.SANDSTONE_SLAB)
        array.schedule_block_add((x, y + 1, z + 2), cls.SANDSTONE_SLAB)
        array.schedule_block_add((x, y + 1, z - 2), cls.SANDSTONE_SLAB)

        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if dx == 0 and dz == 0:
                    array.schedule_block_add((x + dx, y + 4, z + dz), cls.SANDSTONE)
                else:
                    array.schedule_block_add(
                        (x + dx, y + 4, z + dz), cls.SANDSTONE_SLAB
                    )

        for dy in range(1, 3):
            array.schedule_block_add((x - 1, y + dy, z - 1), cls.SANDSTONE)
            array.schedule_block_add((x - 1, y + dy, z + 1), cls.SANDSTONE)
            array.schedule_block_add((x + 1, y + dy, z - 1), cls.SANDSTONE)
            array.schedule_block_add((x + 1, y + dy, z + 1), cls.SANDSTONE)
