import itertools
import typing
import math
from mcpython.util.math import rotate_point
import weakref


# This defines how
CORNER_SIGNS = tuple(itertools.product((-1, 1), repeat=3))
CUBE_MAP = (
    (2, 3, 7, 6),
    (0, 4, 5, 1),
    (0, 1, 3, 2),
    (5, 4, 6, 7),
    (1, 5, 7, 3),
    (4, 0, 2, 6)
)


def calculate_default(size: typing.Tuple[float, float, float]):
    size = tuple(e / 2 for e in size)

    CORNERS = [tuple(e[i] * size[i] for i in range(3)) for e in CORNER_SIGNS]

    return (
        tuple(CORNERS[i] for i in e)
        for e in CUBE_MAP
    )


def offset_data(data, offset: typing.Tuple[float, float, float]):
    return (
        (
            tuple(e[i] + offset[i] for i in range(3))
            for e in x
        )
        for x in data
    )


def rotate_data(data, origin: typing.Tuple[float, float, float], rotation: typing.Tuple[float, float, float]):
    return (
        (
            rotate_point(e, origin, rotation)
            for e in x
        )
        for x in data
    )


class VertexProvider:
    """
    Class doing some magic for vertices calculation

    Invoke create() for getting a shared one, otherwise it will not be made arrival to others

    All attributes are read-only and modification is not part of the public API
    Modification may get made un-arrival in the future

    Use invalidate_internal() to reduce cache load

    todo: can we use some optimised library like numpy here?
    """

    # Internal cache of instances, uses weak references in order to save memory when discarding instances
    # in model system
    SHARED = weakref.WeakValueDictionary()

    @classmethod
    def create(cls, offset: typing.Tuple[float, float, float], size: typing.Tuple[float, float, float], base_rotation_center: typing.Tuple[float, float, float] = None, base_rotation: typing.Tuple[float, float, float] = (0, 0, 0)):
        if base_rotation_center is None:
            base_rotation_center = offset

        # This key defines the VertexProvider instance, so look up this key in the cache
        key = offset, size, base_rotation_center, base_rotation

        # If it exists, we can re-use it
        if key in cls.SHARED:
            return cls.SHARED[key]

        return cls.SHARED.setdefault(key, cls(offset, size, base_rotation_center, base_rotation))

    def __init__(self, offset, size, base_rotation_center, base_rotation):
        self.offset = offset
        self.size = size
        self.base_rotation = base_rotation
        self.base_rotation_center = base_rotation_center

        self.default = tuple(tuple(e) for e in rotate_data(offset_data(calculate_default(size), offset), base_rotation_center, base_rotation))

        # The cache is a structure holding
        self.cache = {}

    def get_vertex_data(self, element_position: typing.Tuple[float, float, float], element_rotation: typing.Tuple[float, float, float]):
        self.ensure_prepared_rotation(element_rotation)

        return list(offset_data(self.cache[element_rotation], element_position))

    def ensure_prepared_rotation(self, rotation: typing.Tuple[float, float, float]):
        if rotation not in self.cache:
            return self.cache.setdefault(rotation, tuple(tuple(e) for e in rotate_data(self.default, (0, 0, 0), rotation)))

        return self.cache[rotation]

    def invalidate_internal(self):
        self.cache.clear()

