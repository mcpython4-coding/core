"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""

import globals as G
import config
import math
import logger


def get_max_y(pos):
    """gets the max y at a x,y,z or x,z pos
    todo: move to Chunk-class"""
    x, y, z = normalize(pos if len(pos) == 3 else (pos[0], 0, pos[1]))
    chunk = G.world.get_active_dimension().get_chunk_for_position((x, y, z))
    heightmap = chunk.get_value('heightmap')
    y = heightmap[x, z][0][1] if (x, z) in heightmap else 0
    return y + config.PLAYER_HEIGHT  # account for the distance from head to foot


def cube_vertices(x, y, z, nx, ny, nz, faces=(True, True, True, True, True, True)):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
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
    return top + bottom + left + right + front + back


def tex_coord(x, y, size=(32, 32), region=(0, 0, 1, 1), rot=0):
    """
    Return the bounding vertices of the texture square.
    :param x: the texture atlas entry to use
    :param y: the texture atlas entry to use
    :param size: the size of the texture atlas used
    :param region: the texture region to use. (0, 0, 1, 1) is full texture atlas texture size
    :param rot: in steps of 90: how much to rotate the vertices
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

    position = []
    [position.extend(e) for e in positions]
    return position


def tex_coords(*args, size=(32, 32), tex_region=None, rotation=(0, 0, 0, 0, 0, 0)):
    """
    Return a list of the texture squares for the top, bottom and sides.
    """
    if tex_region is None: tex_region = [(0, 0, 1, 1)] * 6
    args = list(args)
    for i, arg in enumerate(args):
        if arg is None:
            arg = (0, 0)
        args[i] = arg
    top, bottom, N, S, E, W = tuple(args)
    top = tex_coord(*top, size=size, region=tex_region[0], rot=rotation[0])
    bottom = tex_coord(*bottom, size=size, region=tex_region[1], rot=rotation[1])
    n = tex_coord(*N, size=size, region=tex_region[2], rot=rotation[2])
    e = tex_coord(*E, size=size, region=tex_region[3], rot=rotation[3])
    s = tex_coord(*S, size=size, region=tex_region[4], rot=rotation[4])
    w = tex_coord(*W, size=size, region=tex_region[5], rot=rotation[5])
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(n)
    result.extend(e)
    result.extend(s)
    result.extend(w)
    return result


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

