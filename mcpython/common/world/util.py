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
# Collection of function for working with world
import itertools
import random
import typing

import mcpython.common.world.AbstractInterface
import mcpython.util.math
from mcpython import shared


class BlockSource:
    """
    Helper class for working with blocks
    Contains a list of blocks

    Used for getting and matching blocks

    todo: something global for defining states for block creation
    """

    @classmethod
    def from_any(cls, block: typing.Union[str, "BlockSource"]) -> "BlockSource":
        if hasattr(block, "NAME"):
            # todo: include meta
            return cls().with_block(block.NAME)

        return (
            block if isinstance(block, BlockSource) else BlockSource().with_block(block)
        )

    def __init__(self):
        self.blocks = []

    def with_block(self, block: typing.Optional[str]):
        self.blocks.append(block if isinstance(block, str) else "minecraft:air")
        return self

    def get(self):
        return random.choice(self.blocks)

    def contains(self, instance) -> bool:
        if not isinstance(instance, str):
            instance = instance.NAME if hasattr(instance, "NAME") else "minecraft:air66"

        return instance in self.blocks

    def copy(self):
        instance = BlockSource()
        instance.blocks += self.blocks.copy()
        return instance


class AnyBlock(BlockSource):
    """
    Matcher matching any block
    """

    INSTANCE: typing.Optional["AnyBlock"] = None

    def __init__(self, excludes=None):
        super().__init__()
        self.excludes = excludes if excludes is not None else []

    def get(self):
        # todo: something more efficient here...
        blocks = list(shared.registry.get_by_name("minecraft:block").entries.keys())
        while (b := random.choice(blocks)) not in self.excludes:
            continue
        return b

    def contains(self, instance) -> bool:
        return (
            instance.NAME if hasattr(instance, "NAME") else instance
        ) not in self.excludes

    def with_block(self, block: str):
        self.excludes.append(block)

    def copy(self):
        return AnyBlock(self.excludes.copy())


AnyBlock.INSTANCE = AnyBlock()


def filter_values(
    data: typing.Dict, matcher: BlockSource, inverted=False, to="minecraft:air"
):
    """
    In-place dict value filter using a block source matcher
    :param data: the data, as a dict of any -> matchable
    :param matcher: the BlockSource instance
    :param inverted: if inverted or not
    :param to: what to filter to, so which block to replace with
    """

    for key, value in data.items():
        if matcher.contains(value) == inverted:
            data[key] = to

    return data


def filter_list(
    data: typing.List, matcher: BlockSource, inverted=False, to="minecraft:air"
):
    """
    Filters a list-like structure of block-like elements
    :param data: the list-like
    :param matcher: the matcher
    :param inverted: if inverted
    :param to: filter to
    """

    for i, value in enumerate(data):
        if matcher.contains(value) == inverted:
            data[i] = to

    return data


def area_iterator(start: typing.Tuple[int, int, int], end: typing.Tuple[int, int, int]):
    return itertools.product(*map(lambda e: range(e[0], e[1]+1), zip(start, end)))


def fill_area(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    end: typing.Tuple[int, int, int],
    block: typing.Union[str, BlockSource],
):
    block = BlockSource.from_any(block)

    for p in area_iterator(start, end):
        access.add_block(p, block.get())


def fill_area_replacing(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    end: typing.Tuple[int, int, int],
    block: typing.Union[str, BlockSource],
    replacing: typing.Union[str, BlockSource],
):
    block = BlockSource.from_any(block)
    replacing = BlockSource.from_any(replacing)

    for p in area_iterator(start, end):
        previous = access.get_block(p)

        if replacing.contains(previous):
            access.add_block(p, block.get())


def get_content(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    end: typing.Tuple[int, int, int],
) -> typing.Dict[typing.Tuple[int, int, int], typing.Any]:
    data = {}
    for p in area_iterator(start, end):
        b = access.get_block(p)
        if b is not None and not isinstance(b, str):
            b = b.copy()
        data[
            typing.cast(
                typing.Tuple[int, int, int], mcpython.util.math.vector_offset(p, start)
            )
        ] = b
    return data


def get_content_list(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    end: typing.Tuple[int, int, int],
) -> typing.Iterable:
    for p in area_iterator(start, end):
        b = access.get_block(p)
        if b is not None and not isinstance(b, str):
            b = b.copy()
        yield b


def paste_content(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    data: typing.Dict[typing.Tuple[int, int, int], typing.Any],
    insert_air=True,
    replaces=AnyBlock.INSTANCE,
):
    replaces = AnyBlock.from_any(replaces)

    start = mcpython.util.math.vector_negate(start)
    for p, block in data.items():
        if (
            block is None
            or block == "minecraft:air"
            or (hasattr(block, "NAME"))
            and block.NAME == "minecraft:air"
        ) and not insert_air:
            continue
        p2 = mcpython.util.math.vector_offset(p, start)
        if not replaces.contains(access.get_block(p2)):
            continue
        access.add_block(p2, block)


def paste_content_list(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    end: typing.Tuple[int, int, int],
    data: typing.List[typing.Any],
    insert_air=True,
    replaces=AnyBlock.INSTANCE,
):
    replaces = AnyBlock.from_any(replaces)

    for p, block in zip(area_iterator(start, end), data):
        if (
            block is None
            or block == "minecraft:air"
            or (hasattr(block, "NAME"))
            and block.NAME == "minecraft:air"
        ) and not insert_air:
            continue
        p2 = mcpython.util.math.vector_offset(p, start)
        if not replaces.contains(access.get_block(p2)):
            continue
        access.add_block(p2, block)


def clone(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    end: typing.Tuple[int, int, int],
    to: typing.Tuple[int, int, int],
    block_filter=AnyBlock.INSTANCE,
    replaces=AnyBlock.INSTANCE,
    insert_air=True,
    remove_start=False,
):
    replaces = AnyBlock.from_any(replaces)
    block_filter = AnyBlock.from_any(block_filter)

    start_2, end_2 = mcpython.util.math.sort_components(start, end)
    block_list = list(get_content_list(access, start_2, end_2))
    block_list = filter_list(block_list, block_filter)
    paste_content_list(
        access,
        to,
        mcpython.util.math.vector_offset(
            to, mcpython.util.math.vector_offset(start_2, end_2)
        ),
        block_list,
        insert_air=insert_air,
        replaces=replaces,
    )
    if remove_start:
        fill_area(access, start_2, end_2, "minecraft:air")


def create_hollow_structure(
    access: mcpython.common.world.AbstractInterface.ISupportWorldInterface,
    start: typing.Tuple[int, int, int],
    end: typing.Tuple[int, int, int],
    block: typing.Union[str, BlockSource],
    outline_size=1,
    fill_center=False,
    fill_center_with=None,
):
    """
    Creates a hollow structure
    :param access: the world-like object
    :param start: the start
    :param end: the end
    :param block: the block
    :param outline_size: the width of the structure
    :param fill_center: if the center should be filled
    :param fill_center_with: with this block
    """
    start, end = mcpython.util.math.sort_components(start, end)
    block = BlockSource.from_any(block)
    outline_size -= 1  # We need these as 1 block is 0 offset
    fill_center_with = BlockSource.from_any(fill_center_with)

    x, y, z = start
    dx, dy, dz = mcpython.util.math.vector_offset(start, end)
    fill_area(access, start, (x + dx, y + outline_size, z + dz), block)  # bottom
    fill_area(
        access, (x, y + dy, z), (x + dx, y + dy - outline_size, z + dz), block
    )  # top
    fill_area(
        access,
        (x, y + outline_size + 1, z),
        (x + dx, y + dy - outline_size - 1, z + outline_size),
        block,
    )  # left
    fill_area(
        access,
        (x, y + outline_size + 1, z + dz),
        (x + dx, y + dy - outline_size - 1, z + dz - outline_size),
        block,
    )  # right
    fill_area(
        access,
        (x, y + outline_size + 1, z + outline_size + 1),
        (x + outline_size, y + dy - outline_size - 1, z + dz - outline_size - 1),
        block,
    )  # front
    fill_area(
        access,
        (x + dx, y + outline_size + 1, z + outline_size + 1),
        (x + dx - outline_size, y + dy - outline_size - 1, z + dz - outline_size - 1),
        block,
    )  # back

    if fill_center:
        outline_size += 1  # here we need + 1, as we want the inner
        fill_area(
            access,
            (x + outline_size, y + outline_size, z + outline_size),
            (x + dx - outline_size, y + dy - outline_size, z + dz - outline_size),
            fill_center_with,
        )
