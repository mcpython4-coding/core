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
import itertools
import typing
import weakref

from mcpython.mixin.optimiser_annotations import try_optimise
from mcpython.util.math import rotate_point

# This defines how cubes look; do not change!
CORNER_SIGNS = tuple(itertools.product((-1, 1), repeat=3))
CUBE_MAP = (
    (3, 7, 6, 2),  # UP
    (5, 1, 0, 4),  # DOWN
    (0, 1, 3, 2),  # LEFT
    (5, 4, 6, 7),  # RIGHT
    (1, 5, 7, 3),  # FRONT
    (4, 0, 2, 6),  # BACK
)


@try_optimise()
def calculate_default(size: typing.Tuple[float, float, float]):
    size = tuple(e / 2 for e in size)

    CORNERS = [tuple(e[i] * size[i] for i in range(3)) for e in CORNER_SIGNS]

    return (tuple(CORNERS[i] for i in e) for e in CUBE_MAP)


@try_optimise()
def offset_data(data, offset: typing.Tuple[float, float, float]):
    return ((tuple(e[i] + offset[i] for i in range(3)) for e in x) for x in data)


@try_optimise()
def rotate_data(
    data,
    origin: typing.Tuple[float, float, float],
    rotation: typing.Tuple[float, float, float],
):
    return ((rotate_point(e, origin, rotation) for e in x) for x in data)


@try_optimise()
def scale_data(data, scale: float):
    return ((tuple(e * scale for e in x) for x in y) for y in data)


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
    def create(
        cls,
        offset: typing.Tuple[float, float, float],
        size: typing.Tuple[float, float, float],
        base_rotation_center: typing.Tuple[float, float, float] = None,
        base_rotation: typing.Tuple[float, float, float] = (0, 0, 0),
    ):
        if base_rotation_center is None:
            base_rotation_center = offset

        # This key defines the VertexProvider instance, so look up this key in the cache
        key = offset, size, base_rotation_center, base_rotation

        # If it exists, we can re-use it
        if key in cls.SHARED:
            return cls.SHARED[key]

        return cls.SHARED.setdefault(
            key, cls(offset, size, base_rotation_center, base_rotation)
        )

    def __init__(
        self,
        offset: typing.Tuple[float, float, float],
        size: typing.Tuple[float, float, float],
        base_rotation_center: typing.Tuple[float, float, float],
        base_rotation: typing.Tuple[float, float, float],
    ):
        self.offset = offset
        self.size = size
        self.base_rotation = base_rotation
        self.base_rotation_center = base_rotation_center

        self.default = tuple(
            tuple(e)
            for e in rotate_data(
                offset_data(calculate_default(size), offset),
                base_rotation_center,
                base_rotation,
            )
        )

        # The cache is a structure holding
        self.cache: typing.Dict[
            typing.Tuple[
                typing.Tuple[float, float, float],
                typing.Tuple[float, float, float],
                float,
            ],
            typing.Iterable,
        ] = {}

    @try_optimise()
    def get_vertex_data(
        self,
        element_position: typing.Tuple[float, float, float],
        element_rotation: typing.Tuple[float, float, float] = (0, 0, 0),
        element_rotation_center: typing.Tuple[float, float, float] = None,
        scale: float = 1,
    ):
        self.ensure_prepared_rotation(element_rotation, element_rotation_center, scale)

        return list(
            offset_data(
                self.cache[
                    (element_rotation, element_rotation_center or (0, 0, 0), scale)
                ],
                element_position,
            )
        )

    @try_optimise()
    def ensure_prepared_rotation(
        self,
        rotation: typing.Tuple[float, float, float],
        center: typing.Tuple[float, float, float] = None,
        scale: float = 1,
    ):
        if center is None:
            center = 0, 0, 0

        key = rotation, center, scale

        if key not in self.cache:
            if scale == 1:
                return self.cache.setdefault(
                    key,
                    tuple(
                        tuple(e) for e in rotate_data(self.default, center, rotation)
                    ),
                )
            else:
                return self.cache.setdefault(
                    key,
                    tuple(
                        tuple(e)
                        for e in scale_data(
                            rotate_data(self.default, center, rotation), scale
                        )
                    ),
                )

        return self.cache[key]

    def invalidate_internal(self):
        self.cache.clear()
