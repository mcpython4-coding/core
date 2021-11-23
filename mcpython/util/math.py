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
import functools
import math
import typing
import graphlib

import deprecation
from mcpython.engine import logger


# Use vertex builder
@deprecation.deprecated()
def cube_vertices_better(
    x: float,
    y: float,
    z: float,
    nx: float,
    ny: float,
    nz: float,
    faces=(True, True, True, True, True, True),
) -> typing.Iterable[typing.List[float]]:
    top = (
        [
            x - nx,
            y + ny,
            z - nz,
            x - nx,
            y + ny,
            z + nz,
            x + nx,
            y + ny,
            z + nz,
            x + nx,
            y + ny,
            z - nz,
        ]
        if faces[0]
        else []
    )
    bottom = (
        [
            x - nx,
            y - ny,
            z - nz,
            x + nx,
            y - ny,
            z - nz,
            x + nx,
            y - ny,
            z + nz,
            x - nx,
            y - ny,
            z + nz,
        ]
        if faces[1]
        else []
    )
    left = (
        [
            x - nx,
            y - ny,
            z - nz,
            x - nx,
            y - ny,
            z + nz,
            x - nx,
            y + ny,
            z + nz,
            x - nx,
            y + ny,
            z - nz,
        ]
        if faces[2]
        else []
    )
    right = (
        [
            x + nx,
            y - ny,
            z + nz,
            x + nx,
            y - ny,
            z - nz,
            x + nx,
            y + ny,
            z - nz,
            x + nx,
            y + ny,
            z + nz,
        ]
        if faces[3]
        else []
    )
    front = (
        [
            x - nx,
            y - ny,
            z + nz,
            x + nx,
            y - ny,
            z + nz,
            x + nx,
            y + ny,
            z + nz,
            x - nx,
            y + ny,
            z + nz,
        ]
        if faces[4]
        else []
    )
    back = (
        [
            x + nx,
            y - ny,
            z - nz,
            x - nx,
            y - ny,
            z - nz,
            x - nx,
            y + ny,
            z - nz,
            x + nx,
            y + ny,
            z - nz,
        ]
        if faces[5]
        else []
    )
    return top, bottom, left, right, front, back


def tex_coordinates(x, y, size=(32, 32), region=(0, 0, 1, 1), rot=0) -> tuple:
    """
    Return the bounding vertices of the texture square.
    :param x: the texture atlas entry to use
    :param y: the texture atlas entry to use
    :param size: the size of the texture atlas used
    :param region: the texture region to use. (0, 0, 1, 1) is full texture atlas texture size
    :param rot: in steps of 90: how much to rotate the vertices
    :return: a tuple representing the texture coordinates
    """
    mx = 1.0 / size[0]
    my = 1.0 / size[1]
    dx = x * mx
    dy = y * my
    bx, by, ex, ey = (
        region[0] / size[0],
        region[1] / size[1],
        (1 - region[2]) / size[0],
        (1 - region[3]) / size[1],
    )
    positions = [
        (dx + bx, dy + by),
        (dx + mx - ex, dy + by),
        (dx + mx - ex, dy + my - ey),
        (dx + bx, dy + my - ey),
    ]

    if rot != 0:
        reindex = rot // 90
        _positions = positions
        positions = [0] * len(positions)
        for i, e in enumerate(_positions):
            positions[(i + reindex) % 4] = e

    return sum(positions, tuple())


def tex_coordinates_better(
    *args: typing.Tuple[int, int],
    size=(32, 32),
    tex_region=None,
    rotation=(0, 0, 0, 0, 0, 0)
) -> list:
    """
    This is a better implementation of above tex_coords function. It will return a list of coords instead
        of a list where you have to manually find entries for drawing
    :param args: for each face to calculate, the uv's as a tuple of size 2
    :param size: the size of the texture group, as specified by the texture atlas
    :param tex_region: the region in the texture, where 0 is one end and 1 the other
    :param rotation: the rotation of the whole thing
    :return: a list of lists of texture coords
    """
    if tex_region is None:
        tex_region = [(0, 0, 1, 1)] * len(args)

    return [
        tex_coordinates(
            *(face if face is not None else (0, 0)),
            size=size,
            region=tex_region[i],
            rot=rotation[i]
        )
        for i, face in enumerate(args)
    ]


def normalize(position: typing.Tuple[float, float, float]):
    """
    Accepts `position` of arbitrary precision and returns the block
    containing that position

    Uses simply rounding on all components

    :param position: the position
    :return: the rounded position
    """
    try:
        return tuple(round(e) for e in position)
    except:
        logger.println("[FATAL] error during parsing position {}".format(position))
        raise


def position_to_chunk(
    position: typing.Union[
        typing.Tuple[float, float, float], typing.Tuple[float, float]
    ]
) -> typing.Tuple[int, int]:
    """
    Returns a tuple representing the chunk for the given `position`.
    :param position: the position, as a two-tuple (x, z) or three-tuple (x, y, z)
    :return: the chunk position, as (x, z)
    """
    x, *_, z = position
    x, z = x // 16, z // 16
    return int(x), int(z)


# code from https://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list
@deprecation.deprecated()
def topological_sort(items):
    """
    'items' is an iterable of (item, dependencies) pairs, where 'dependencies'
    is an iterable of the same type as 'items'.

    If 'items' is a generator rather than a data structure, it should not be
    empty. Passing an empty generator for 'items' (zero yields before return)
    will cause topological_sort() to raise TopologicalSortFailure.

    An empty iterable (e.g. list, tuple, set, ...) produces no items but
    raises no exception.

    todo: replace with native sorting system
    """
    generator = graphlib.TopologicalSorter()
    for key, dep in items:
        generator.add(key, *dep)
    return list(generator.static_order())


def rotate_point(point, origin, rotation):
    """
    Helper function for rotating an point around another one
    :param point: the point to rotate
    :param origin: the origin to rotate around
    :param rotation: the rotation angle
    :return: the rotated point

    todo: optimise!
    """
    # code translated from https://stackoverflow.com/questions/13275719/rotate-a-3d-point-around-another-one
    x, y, z = point
    ox, oy, oz = origin
    rx, ry, rz = rotation
    rx = math.pi * rx / 180
    ry = math.pi * ry / 180
    rz = math.pi * rz / 180
    x -= ox
    y -= oy
    z -= oz

    nx = x * math.cos(rz) - y * math.sin(rz)
    ny = x * math.sin(rz) + y * math.cos(rz)
    x, y = nx, ny

    nx = x * math.cos(ry) - z * math.sin(ry)
    nz = x * math.sin(ry) + z * math.cos(ry)
    x, z = nx, nz

    ny = y * math.cos(rx) - z * math.sin(rx)
    nz = y * math.sin(rx) + z * math.cos(rx)
    y, z = ny, nz

    return x + ox, y + oy, z + oz


def product(iterable: typing.List[typing.SupportsFloat]):
    """
    Same as sum(), but will use * instead of +
    """
    return functools.reduce(lambda x, y: x + y, iterable)


def vector_offset(
    vector: typing.Tuple[float, ...], base: typing.Tuple[float, ...]
) -> typing.Tuple[float, ...]:
    return tuple(a - b for a, b in zip(vector, base))


def vector_negate(vector: typing.Tuple[float, ...]) -> typing.Tuple[float, ...]:
    return tuple(-e for e in vector)


def vector_distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))


def sort_components(a: typing.Tuple[float, ...], b: typing.Tuple[float, ...]):
    """
    Util method for sorting two vectors
    :return: two tuples, one with the smallest x, y, z and one with the biggest x, y, z coordinate

    Example:
    sort_components((-1, 5, -7), (5, -10, 4)) == ((-1, -10, -7), (5, 5, 4))

    Useful when user inputs two coordinates and usage requires this special order (for example, for range()-ing over them)
    """
    return tuple(zip(*map(lambda e: (min(e), max(e)), zip(a, b))))
