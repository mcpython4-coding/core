"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import util.math
import pyglet.gl


class BoundingBox:
    def __init__(self, size, relposition=(0, 0, 0)):
        self.size = size
        self.relposition = relposition

    def test_point_hit(self, point, boxposition):
        x, y, z = tuple([r / 2 for r in self.size])
        dx, dy, dz = tuple([abs(boxposition[i] + self.relposition[i] - point[i]) for i in range(3)])
        return dx <= x and dy <= y and dz <= z

    def draw_outline(self, position):
        x, y, z = position
        x += self.relposition[0] - 0.5 + (self.size[0] / 2)
        y += self.relposition[1] - 0.5 + (self.size[1] / 2)
        z += self.relposition[2] - 0.5 + (self.size[2] / 2)
        vertex_data = util.math.cube_vertices(x, y, z, *[f/2+0.005 for f in self.size])
        pyglet.gl.glColor3d(0, 0, 0)
        # glLineWidth(1.5)
        pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE)
        pyglet.graphics.draw(24, pyglet.gl.GL_QUADS, ('v3f/static', vertex_data))
        pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_FILL)


class BoundingArea:
    """
    more options for hit-test by using an list of BoundBoxes. Has the same methods for interaction
    """

    def __init__(self):
        self.bboxes = []

    def add_box(self, size, relposition=(0, 0, 0)):
        self.bboxes.append(BoundingBox(size, relposition=relposition))

    def test_point_hit(self, point, boxposition):
        for bbox in self.bboxes:
            if bbox.test_point_hit(point, boxposition): return True
        return False

    def draw_outline(self, position): [bbox.draw_outline(position) for bbox in self.bboxes]


FULL_BLOCK_BOUNDING_BOX = BoundingBox((1, 1, 1))

