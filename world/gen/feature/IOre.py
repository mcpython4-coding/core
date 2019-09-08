"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import world.gen.feature.IFeature
import enum
import world.Dimension
import random


def place_default(x: int, y: int, z: int, sx: int, sy: int, sz: int, blocks: list, replace: list,
                  dimension: world.Dimension.Dimension):
    for dx in range(sx, sx+1):
        for dy in range(sy, sy+1):
            for dz in range(sz, sz+1):
                if dx ** 2 / sx ** 2 + dy ** 2 / sy ** 2 + dz ** 2 / sz ** 2 <= 1:
                    rx, ry, rz = dx + x, dy + y, dz + z
                    block = dimension.get_block((rx, ry, rz))
                    name = block.get_name() if block else None
                    if name in replace:
                        dimension.get_chunk_for_position((rx, ry, rz)).add_add_block_gen_task(
                            (rx, ry, rz), random.choice(blocks))


class OrePlacementMode(enum.Enum):
    DEFAULT = 0  # args: minh, maxh
    MIDDLE_HIGHEST = 1  # args: minh, maxh, minchance


class IOre(world.gen.feature.IFeature.IFeature):
    @staticmethod
    def place(dimension, x, y, z, **config):
        pass

    @staticmethod
    def get_height_range() -> tuple: raise NotImplementedError()

    @staticmethod
    def get_ore_block() -> str or list:
        """
        :return: an orename or an list of orenames or an {orename: chance} table
        """
        raise NotImplementedError()

    @staticmethod
    def get_replacement_blocks(): return ["minecraft:stone"]

    @staticmethod
    def get_size_range() -> tuple: raise NotImplementedError()

    @staticmethod
    def get_chunk_count() -> int: raise NotImplementedError()

    @staticmethod
    def get_ore_height() -> int: raise NotImplementedError()


class INormalOre(IOre):
    @classmethod
    def place(cls, dimension, x, y, z, **config):
        size = round(random.randint(*cls.get_size_range()) ** (1 / 3))
        rx, ry, rz = random.randint(1, size), random.randint(1, size), random.randint(1, size)
        ores = cls.get_ore_block()
        if type(ores) == str: ores = [ores]
        place_default(x, y, z, rx, ry, rz, ores, cls.get_replacement_blocks(), dimension)

    @classmethod
    def get_ore_height(cls) -> int:
        return random.randint(*cls.get_height_range())


class CoalOre(INormalOre):
    @staticmethod
    def get_size_range() -> tuple: return 4, 17

    @staticmethod
    def get_chunk_count() -> int: return 20

    @staticmethod
    def get_height_range() -> tuple: return 0, 127

    @staticmethod
    def get_ore_block() -> str or list: return "minecraft:coal_ore"

