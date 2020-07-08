"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.util.math
import pyglet.gl
import mcpython.rendering.OpenGLSetupFile


class BoundingBox:
    def __init__(self, size, relposition=(0, 0, 0), rotation=(0, 0, 0)):
        self.size = size
        self.relposition = relposition
        self.rotation = rotation

    def test_point_hit(self, point, boxposition):
        point = mcpython.util.math.rotate_point(point, tuple([boxposition[i] + self.relposition[i] for i in range(3)]),
                                       rotation=self.rotation)
        x, y, z = point
        sx, sy, sz = tuple([boxposition[i] - 0.5 + self.relposition[i] for i in range(3)])
        ex, ey, ez = tuple([boxposition[i] - 0.5 + self.relposition[i] + self.size[i] for i in range(3)])
        return sx <= x <= ex and sy <= y <= ey and sz <= z <= ez

    def draw_outline(self, position):
        rot = tuple([-e for e in self.rotation])
        x, y, z = position
        x += self.relposition[0] - 0.5 + (self.size[0] / 2)
        y += self.relposition[1] - 0.5 + (self.size[1] / 2)
        z += self.relposition[2] - 0.5 + (self.size[2] / 2)
        vertex_data_ur = mcpython.util.math.cube_vertices(0, 0, 0, *[f/2+0.001 for f in self.size])
        vertex_data = []
        for i in range(len(vertex_data_ur) // 3):
            nx, ny, nz = x, y, z
            rx, ry, rz = mcpython.util.math.rotate_point(vertex_data_ur[i*3:i*3+3], (0, 0, 0), rot)
            vertex_data.extend([nx+rx, ny+ry, nz+rz])
        mcpython.rendering.OpenGLSetupFile.execute_file_by_name("draw_line_box", vertex=('v3f/static', vertex_data))


class BoundingArea:
    """
    more options for hit-test by using an list of BoundBoxes. Has the same methods for interaction
    """

    def __init__(self):
        self.bboxes = []

    def add_box(self, size, relposition=(0, 0, 0), rotation=(0, 0, 0)):
        self.bboxes.append(BoundingBox(size, relposition=relposition, rotation=rotation))
        return self

    def test_point_hit(self, point, boxposition):
        for bbox in self.bboxes:
            if bbox.test_point_hit(point, boxposition): return True
        return False

    def draw_outline(self, position): [bbox.draw_outline(position) for bbox in self.bboxes]


FULL_BLOCK_BOUNDING_BOX = BoundingBox((1, 1, 1))

