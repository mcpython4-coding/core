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
import typing
from abc import ABC

import mcpython.engine.rendering.util
import mcpython.util.math


class AbstractBoundingBox(ABC):
    """
    Abstract base class for bounding-box like classes
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


class BoundingBox(AbstractBoundingBox):
    """
    The basic bounding box - a cube
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

    def test_point_hit(
        self,
        point: typing.Tuple[float, float, float],
        boxposition: typing.Tuple[float, float, float],
    ):
        point = mcpython.util.math.rotate_point(
            point,
            tuple([boxposition[i] + self.relative_position[i] for i in range(3)]),
            rotation=self.rotation,
        )
        x, y, z = point
        sx, sy, sz = tuple(
            [boxposition[i] - 0.5 + self.relative_position[i] for i in range(3)]
        )
        ex, ey, ez = tuple(
            [
                boxposition[i] - 0.5 + self.relative_position[i] + self.size[i]
                for i in range(3)
            ]
        )
        return sx <= x <= ex and sy <= y <= ey and sz <= z <= ez

    def draw_outline(self, position: typing.Tuple[float, float, float]):
        rot = tuple([-e for e in self.rotation])
        x, y, z = position
        x += self.relative_position[0] - 0.5 + (self.size[0] / 2)
        y += self.relative_position[1] - 0.5 + (self.size[1] / 2)
        z += self.relative_position[2] - 0.5 + (self.size[2] / 2)
        vertex_data_ur = sum(
            mcpython.util.math.cube_vertices_better(
                0, 0, 0, *[f / 2 + 0.001 for f in self.size]
            ),
            [],
        )
        vertex_data = []
        for i in range(len(vertex_data_ur) // 3):
            nx, ny, nz = x, y, z
            rx, ry, rz = mcpython.util.math.rotate_point(
                vertex_data_ur[i * 3 : i * 3 + 3], (0, 0, 0), rot
            )
            vertex_data.extend([nx + rx, ny + ry, nz + rz])
        mcpython.engine.rendering.util.draw_line_box(("v3f/static", vertex_data))


class BoundingArea(AbstractBoundingBox):
    """
    More options for hit-test by using an list of BoundBoxes. Has the same methods for interaction
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
