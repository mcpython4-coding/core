"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""

import globals as G
import mcpython.config
import math
import logger
import deprecation
import deprecation


@deprecation.deprecated("dev3-2", "a1.3.0")
def get_max_y(pos):
    x, y, z = normalize(pos if len(pos) == 3 else (pos[0], 0, pos[1]))
    chunk = G.world.get_active_dimension().get_chunk_for_position((x, y, z))
    return chunk.get_maximum_y_coordinate_from_generation(*pos)


@deprecation.deprecated(deprecated_in="snapshot dev 1 cycle 1", removed_in="v1.2.0 alpha")
def cube_vertices(x, y, z, nx, ny, nz, faces=(True, True, True, True, True, True)):
    """
    Same as cube_vertices_better, but will return all summed up instead of separated lists
    """
    return sum(cube_vertices_better(x, y, z, nx, ny, nz, faces=faces), [])


def cube_vertices_better(x, y, z, nx, ny, nz, faces=(True, True, True, True, True, True)):
    top = [x - nx, y + ny, z - nz, x - nx, y + ny, z + nz, x + nx, y + ny, z + nz, x + nx, y + ny, z - nz] if faces[0] \
        else []
    bottom = [x - nx, y - ny, z - nz, x + nx, y - ny, z - nz, x + nx, y - ny, z + nz, x - nx, y - ny, z + nz] if \
        faces[1] else []
    left = [x - nx, y - ny, z - nz, x - nx, y - ny, z + nz, x - nx, y + ny, z + nz, x - nx, y + ny, z - nz] if \
        faces[2] else []
    right = [x + nx, y - ny, z + nz, x + nx, y - ny, z - nz, x + nx, y + ny, z - nz, x + nx, y + ny, z + nz] if \
        faces[3] else []
    front = [x - nx, y - ny, z + nz, x + nx, y - ny, z + nz, x + nx, y + ny, z + nz, x - nx, y + ny, z + nz] if \
        faces[4] else []
    back = [x + nx, y - ny, z - nz, x - nx, y - ny, z - nz, x - nx, y + ny, z - nz, x + nx, y + ny, z - nz] if \
        faces[5] else []
    return top, bottom, left, right, front, back


def tex_coord(x, y, size=(32, 32), region=(0, 0, 1, 1), rot=0) -> tuple:
    """
    Return the bounding vertices of the texture square.
    :param x: the texture atlas entry to use
    :param y: the texture atlas entry to use
    :param size: the size of the texture atlas used
    :param region: the texture region to use. (0, 0, 1, 1) is full texture atlas texture size
    :param rot: in steps of 90: how much to rotate the vertices
    :return: an tuple representing the texture coordinates
    """
    mx = 1. / size[0]
    my = 1. / size[1]
    dx = x * mx
    dy = y * my
    bx, by, ex, ey = region[0] / size[0], region[1] / size[1], (1 - region[2]) / size[0], (1 - region[3]) / size[1]
    positions = [(dx + bx, dy + by), (dx + mx - ex, dy + by), (dx + mx - ex, dy + my - ey), (dx + bx, dy + my - ey)]
    if rot != 0:
        reindex = rot // 90
        _positions = positions
        positions = [0] * len(positions)
        for i, e in enumerate(_positions):
            positions[(i+reindex) % 4] = e
    return sum(positions, tuple())


@deprecation.deprecated(deprecated_in="snapshot dev 1 cycle 1", removed_in="v1.2.0 alpha")
def tex_coords(*args, size=(32, 32), tex_region=None, rotation=(0, 0, 0, 0, 0, 0)):
    """
    same as tex_coords_better, but returns everything in an single list instead of an list of tuples
    todo: when removed, rename later the new one to this
    """
    return sum(tex_coords_better(*args, size=size, tex_region=tex_region, rotation=rotation), tuple())


def tex_coords_better(*args, size=(32, 32), tex_region=None, rotation=(0, 0, 0, 0, 0, 0)) -> list:
    """
    this is an better implementation of above tex_coords function. It will return an list of coords instead
    of an list where you have to manually find entries
    :param args: every face to calculate
    :param size: the size of the texture group
    :param tex_region: the region in the texture, where 0 is one end and 1 the other
    :param rotation: the rotation of the whole thing
    :return: an list of lists of texture coords
    """
    if tex_region is None: tex_region = [(0, 0, 1, 1)] * len(args)
    return [tex_coord(*(face if face is not None else (0, 0)), size=size, region=tex_region[i], rot=rotation[i])
            for i, face in enumerate(args)]


def tex_coord_factor(fx, fy, tx, ty): return fx, fy, tx, fy, tx, ty, fx, ty


def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    try:
        x, y, z = position if type(position) == tuple else tuple(position)
        x, y, z = (int(round(x)), int(round(y)), int(round(z)))
        return x, y, z
    except:
        logger.println(position)
        raise


def normalize_ceil(position):
    try:
        x, y, z = position if type(position) == tuple else tuple(position)
        x, y, z = (int(math.ceil(x)), int(math.ceil(y)), int(math.ceil(z)))
        return x, y, z
    except:
        logger.println(position)
        raise


def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, z = x // 16, z // 16
    return x, z


# code from https://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list
def topological_sort(items):
    """
    'items' is an iterable of (item, dependencies) pairs, where 'dependencies'
    is an iterable of the same type as 'items'.

    If 'items' is a generator rather than a data structure, it should not be
    empty. Passing an empty generator for 'items' (zero yields before return)
    will cause topological_sort() to raise TopologicalSortFailure.

    An empty iterable (e.g. list, tuple, set, ...) produces no items but
    raises no exception.
    """
    provided = set()
    while items:
        remaining_items = []
        emitted = False

        for item, dependencies in items:
            if provided.issuperset(dependencies):
                yield item
                provided.add(item)
                emitted = True
            else:
                remaining_items.append((item, dependencies))

        if not emitted:
            logger.println("[TOPOSORT][FATAL] failed to sort dependency graph {}".format(items))
            raise ValueError()

        items = remaining_items


def rotate_point(point, origin, rotation):
    # code translated from https://stackoverflow.com/questions/13275719/rotate-a-3d-point-around-another-one
    x, y, z = point
    ox, oy, oz = origin
    rx, ry, rz = rotation
    rx = math.pi * rx / 180
    ry = math.pi * ry / 180
    rz = math.pi * rz / 180
    x -= ox; y -= oy; z -= oz

    nx = x*math.cos(rz) - y*math.sin(rz)
    ny = x*math.sin(rz) + y*math.cos(rz)
    x, y = nx, ny

    nx = x * math.cos(ry) - z * math.sin(ry)
    nz = x * math.sin(ry) + z * math.cos(ry)
    x, z = nx, nz

    ny = y * math.cos(rx) - z * math.sin(rx)
    nz = y * math.sin(rx) + z * math.cos(rx)
    y, z = ny, nz

    return x + ox, y + oy, z + oz

