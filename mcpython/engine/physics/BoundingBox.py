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
        boxposition: typing.Tuple[float, float, float],
    ):
        """
        Tests for a collision with a single point
        :param point: the point
        :param boxposition: the offset of the box
        """
        raise NotImplementedError()

    def draw_outline(self, position: typing.Tuple[float, float, float]):
        """
        Draws an outline of the box
        :param position: the offset of the box
        """
        raise NotImplementedError()

    def get_collision_motion_vector(self, this_position: typing.Tuple[float, float, float], collision_with: "AbstractBoundingBox", that_position: typing.Tuple[float, float, float]) -> typing.Tuple[float, float, float]:
        """
        Optional method implementing an algorithm for collision, where self is the moving body, and
        the parameter is the stationary body

        Returns a motion vector for self to move to not collide with the body
        """
        raise RuntimeError


class BoundingBox(AbstractBoundingBox):
    """
    The basic bounding box - an axis aligned cube
    """

    def __init__(
        self,
        size: typing.Tuple[float, float, float],
        relative_position: typing.Tuple[float, float, float] = (0, 0, 0),
        rotation: typing.Tuple[float, float, float] = (0, 0, 0),
    ):
        self.size = size
        self.relative_position = relative_position
        self.rotation = rotation

        self.vertex_provider = VertexProvider.create(
            typing.cast(
                typing.Tuple[float, float, float],
                tuple(
                    self.relative_position[i] + self.size[i] / 2 - 0.5 for i in range(3)
                ),
            ),
            size,
            (0, 0, 0),
            rotation,
        )

    def recalculate_vertices(self):
        self.vertex_provider = VertexProvider.create(
            self.relative_position, self.size, (0, 0, 0), self.rotation
        )

    def test_point_hit(
        self,
        point: typing.Tuple[float, float, float],
        box_position: typing.Tuple[float, float, float],
    ):
        point = mcpython.util.math.rotate_point(
            point,
            tuple([box_position[i] + self.relative_position[i] for i in range(3)]),
            rotation=self.rotation,
        )
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

    def get_collision_motion_vector(self, this_position: typing.Tuple[float, float, float], collision_with: "AbstractBoundingBox", that_position: typing.Tuple[float, float, float]):
        if isinstance(collision_with, BoundingBox):
            return tuple(
                self.get_collision_vector_component(this_position[i]+self.relative_position[i], self.size[i], that_position[i]+collision_with.relative_position[i], collision_with.size[i])
                for i in range(3)
            )

        else:
            raise RuntimeError

    @classmethod
    def get_collision_vector_component(cls, x: float, sx: float, y: float, sy: float) -> float:
        # Distance between two centers less than the sum of both sizes
        if abs(x - y) < sx + sy:
            if x > y:
                return sy - abs(x - y)
            else:
                return -(sy - abs(x - y))

        # No collision
        return 0


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
        rotation=(0, 0, 0),
    ):
        self.bounding_boxes.append(
            BoundingBox(size, relative_position=relative_position, rotation=rotation)
        )
        return self

    def test_point_hit(
        self,
        point: typing.Tuple[float, float, float],
        boxposition: typing.Tuple[float, float, float],
    ):
        for bbox in self.bounding_boxes:
            if bbox.test_point_hit(point, boxposition):
                return True
        return False

    def draw_outline(self, position: typing.Tuple[float, float, float]):
        [bbox.draw_outline(position) for bbox in self.bounding_boxes]


FULL_BLOCK_BOUNDING_BOX = BoundingBox((1, 1, 1))
EMPTY_BOUNDING_BOX = BoundingArea()
