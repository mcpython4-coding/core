"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

import globals as G


def get_max_y(pos):
    """gets the max y at a x,y,z or x,z pos"""
    x, y, z = normalize(pos if len(pos) == 3 else (pos[0], 0, pos[1]))
    chunk = G.world.get_active_dimension().get_chunk_for_position(pos)
    heightmap = chunk.get_value('heightmap')
    y = heightmap[x, z][0][1]
    return y + 2  # account for the distance from head to foot


def cube_vertices(x, y, z, n, faces=(True, True, True, True, True, True)):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    top = [x - n, y + n, z - n, x - n, y + n, z + n, x + n, y + n, z + n, x + n, y + n, z - n] if faces[0] else []
    bottom = [x - n, y - n, z - n, x + n, y - n, z - n, x + n, y - n, z + n, x - n, y - n, z + n] if faces[1] else []
    left = [x - n, y - n, z - n, x - n, y - n, z + n, x - n, y + n, z + n, x - n, y + n, z - n] if faces[2] else []
    right = [x + n, y - n, z + n, x + n, y - n, z - n, x + n, y + n, z - n, x + n, y + n, z + n] if faces[3] else []
    front = [x - n, y - n, z + n, x + n, y - n, z + n, x + n, y + n, z + n, x - n, y + n, z + n] if faces[4] else []
    back = [x + n, y - n, z - n, x - n, y - n, z - n, x - n, y + n, z - n, x + n, y + n, z - n] if faces[5] else []
    return top + bottom + left + right + front + back


def cube_vertices_2(x, y, z, nx, ny, nz, faces=(True, True, True, True, True, True)):
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


def tex_coord(x, y, n=16):
    """ Return the bounding vertices of the texture square.

    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


def tex_coords_2(*args):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    args = list(args)
    for i, arg in enumerate(args):
        if arg is None:
            arg = (0, 0)
        args[i] = arg
    top, bottom, N, E, W, S = tuple(args)
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    n = tex_coord(*N)
    e = tex_coord(*E)
    s = tex_coord(*S)
    w = tex_coord(*W)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(n)
    result.extend(e)
    result.extend(s)
    result.extend(w)
    return result


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
        print(position)
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
