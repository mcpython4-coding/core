"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""


def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x - n, y + n, z - n, x - n, y + n, z + n, x + n, y + n, z + n, x + n, y + n, z - n,  # top
        x - n, y - n, z - n, x + n, y - n, z - n, x + n, y - n, z + n, x - n, y - n, z + n,  # bottom
        x - n, y - n, z - n, x - n, y - n, z + n, x - n, y + n, z + n, x - n, y + n, z - n,  # left
        x + n, y - n, z + n, x + n, y - n, z - n, x + n, y + n, z - n, x + n, y + n, z + n,  # right
        x - n, y - n, z + n, x + n, y - n, z + n, x + n, y + n, z + n, x - n, y + n, z + n,  # front
        x + n, y - n, z - n, x - n, y - n, z - n, x - n, y + n, z - n, x + n, y + n, z - n,  # back
    ]


def cube_vertices_2(x, y, z, nx, ny, nz):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x - nx, y + ny, z - nz, x - nx, y + ny, z + nz, x + nx, y + ny, z + nz, x + nx, y + ny, z - nz,  # top
        x - nx, y - ny, z - nz, x + nx, y - ny, z - nz, x + nx, y - ny, z + nz, x - nx, y - ny, z + nz,  # bottom
        x - nx, y - ny, z - nz, x - nx, y - ny, z + nz, x - nx, y + ny, z + nz, x - nx, y + ny, z - nz,  # left
        x + nx, y - ny, z + nz, x + nx, y - ny, z - nz, x + nx, y + ny, z - nz, x + nx, y + ny, z + nz,  # right
        x - nx, y - ny, z + nz, x + nx, y - ny, z + nz, x + nx, y + ny, z + nz, x - nx, y + ny, z + nz,  # front
        x + nx, y - ny, z - nz, x - nx, y - ny, z - nz, x - nx, y + ny, z - nz, x + nx, y + ny, z - nz,  # back
    ]


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
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return x, y, z


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

