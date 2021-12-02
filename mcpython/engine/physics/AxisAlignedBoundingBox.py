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
from abc import ABC
from functools import reduce

import mcpython.engine.rendering.util
import mcpython.util.math
from mcpython.util.vertex import VertexProvider


class AbstractBoundingBox(ABC):
    """
    Abstract base class for bounding-box like classes to use in the corresponding systems
    """

    def test_point_hit(
        self,
        point: typing.Tuple[float, float, float],
        box_position: typing.Tuple[float, float, float],
    ):
        """
        Tests for a collision with a single point
        :param point: the point
        :param box_position: the offset of the box
        """
        raise NotImplementedError()

    def draw_outline(self, position: typing.Tuple[float, float, float]):
        """
        Draws an outline of the box
        :param position: the offset of the box
        """
        raise NotImplementedError()

    def get_collision_motion_vector(
        self,
        this_position: typing.Tuple[float, float, float],
        collision_with: "AbstractBoundingBox",
        that_position: typing.Tuple[float, float, float],
    ) -> typing.Tuple[float, float, float]:
        """
        Optional method implementing an algorithm for collision, where self is the moving body, and
        the parameter is the stationary body

        Returns a motion vector for self to move to not collide with the body
        """
        raise RuntimeError


class AxisAlignedBoundingBox(AbstractBoundingBox):
    """
    The basic bounding box - an axis aligned cube
    """

    def __init__(
        self,
        size: typing.Tuple[float, float, float],
        relative_position: typing.Tuple[float, float, float] = (0, 0, 0),
    ):
        self.size = size
        self.relative_position = relative_position

        self.vertex_provider = VertexProvider.create(
            typing.cast(
                typing.Tuple[float, float, float],
                tuple(
                    self.relative_position[i] + self.size[i] / 2 - 0.5 for i in range(3)
                ),
            ),
            size,
            (0, 0, 0),
            (0, 0, 0),
        )

    def recalculate_vertices(self):
        self.vertex_provider = VertexProvider.create(
            self.relative_position, self.size, (0, 0, 0), (0, 0, 0)
        )

    def test_point_hit(
        self,
        point: typing.Tuple[float, float, float],
        box_position: typing.Tuple[float, float, float],
    ):
        x, y, z = point
        sx, sy, sz = tuple(
            [box_position[i] - 0.5 + self.relative_position[i] for i in range(3)]
        )
        ex, ey, ez = tuple(
            [
                box_position[i] - 0.5 + self.relative_position[i] + self.size[i]
                for i in range(3)
            ]
        )
        return sx <= x <= ex and sy <= y <= ey and sz <= z <= ez

    def draw_outline(self, position: typing.Tuple[float, float, float]):
        mcpython.engine.rendering.util.draw_line_box(
            (
                "v3f/static",
                sum(
                    itertools.chain(*self.vertex_provider.get_vertex_data(position)),
                    tuple(),
                ),
            )
        )

    def get_collision_motion_vector(
        self,
        this_position: typing.Tuple[float, float, float],
        collision_with: "AbstractBoundingBox",
        that_position: typing.Tuple[float, float, float],
    ):
        if isinstance(collision_with, AxisAlignedBoundingBox):
            return tuple(
                self.get_collision_vector_component(
                    this_position[i] + self.relative_position[i],
                    self.size[i],
                    that_position[i] + collision_with.relative_position[i],
                    collision_with.size[i],
                )
                for i in range(3)
            )

        else:
            raise RuntimeError

    @classmethod
    def get_collision_vector_component(
        cls, x: float, sx: float, y: float, sy: float
    ) -> float:
        # Distance between two centers less than the sum of both sizes
        if abs(x - y) < sx + sy:
            if x > y:
                return sy - abs(x - y)
            else:
                return -(sy - abs(x - y))

        # No collision
        return 0

    def test_collision_with(
        self, this_position, that_position, box: "AxisAlignedBoundingBox"
    ) -> int:
        v = reduce(
            lambda a, b: a * b,
            [
                self.collides_in_dimension(a, b, i, box)
                for a, b, i in zip(this_position, that_position, range(3))
            ],
        )
        return v

    def collides_in_dimension(
        self,
        this_position: int,
        that_position: int,
        dim: int,
        box: "AxisAlignedBoundingBox",
    ) -> int:
        mx = this_position
        mx += self.relative_position[dim]
        msx = self.size[dim]

        tx = that_position
        tx += box.relative_position[dim]
        mtx = box.size[dim]

        ax, bx = mx - msx / 2, mx + msx / 2
        cx, dx = tx - mtx / 2, tx + mtx / 2

        if ax > dx or bx < cx:
            return 0
        if ax <= cx and dx <= bx:
            return mtx
        if ax >= cx and dx >= bx:
            return msx

        if ax <= cx <= bx:
            return bx - cx
        if ax >= cx >= bx:
            return ax - cx

        raise RuntimeError()


class BoundingArea(AbstractBoundingBox):
    """
    More options for hit-test by using a list of BoundBoxes
    """

    def __init__(self):
        self.bounding_boxes = []

    def add_box(
        self,
        size: typing.Tuple[float, float, float],
        relative_position=(0, 0, 0),
    ):
        self.bounding_boxes.append(
            AxisAlignedBoundingBox(size, relative_position=relative_position)
        )
        return self

    def test_point_hit(
        self,
        point: typing.Tuple[float, float, float],
        box_position: typing.Tuple[float, float, float],
    ):
        for bbox in self.bounding_boxes:
            if bbox.test_point_hit(point, box_position):
                return True
        return False

    def draw_outline(self, position: typing.Tuple[float, float, float]):
        [bbox.draw_outline(position) for bbox in self.bounding_boxes]


FULL_BLOCK_BOUNDING_BOX = AxisAlignedBoundingBox((1, 1, 1))
EMPTY_BOUNDING_BOX = BoundingArea()
