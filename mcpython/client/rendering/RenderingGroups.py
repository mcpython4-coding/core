"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import pyglet
import mcpython.client.rendering.MatrixStack
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class CollectionGroup(pyglet.graphics.Group):
    """
    Group of groups
    """

    def __init__(self, *sub_groups):
        super().__init__()
        self.sub_groups = sub_groups

    def set_state(self):
        [group.set_state() for group in self.sub_groups]

    def unset_state(self):
        [group.unset_state() for group in self.sub_groups]


@onlyInClient()
class MatrixStackGroup(pyglet.graphics.Group):
    """
    Group for holding an custom MatrixStack-instance
    """

    def __init__(self, stack: mcpython.client.rendering.MatrixStack.MatrixStack):
        super().__init__()
        self.stack = stack

    def set_state(self):
        self.stack.apply()

    def unset_state(self):
        pass


@onlyInClient()
class ScissorGroup(pyglet.graphics.Group):
    """
    Code by: pyglet
    url: https://github.com/pyglet/pyglet/blob/pyglet-1.5-maintenance/examples/opengl/opengl_scissor.py

    A Custom Group that defines a "Scissor" area.
    If a Sprite/Label is in this Group, any parts of it that
    fall outside of the specified area will not be drawn.
    NOTE: You should use the same exact group instance
    for every object that will use the group, equal groups
    will still be kept seperate.
    :Parameters:
        `x` : int
            The X coordinate of the Scissor area.
        `x` : int
            The X coordinate of the Scissor area.
        `width` : int
            The width of the Scissor area.
        `height` : int
            The height of the Scissor area.
    """

    def __init__(self, x, y, width, height, parent=None):
        super().__init__(parent)
        self.x, self.y = x, y
        self.width, self.height = width, height

    @property
    def area(self):
        return self.x, self.y, self.width, self.height

    @area.setter
    def area(self, area):
        self.x, self.y, self.width, self.height = area

    def set_state(self):
        pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST)
        pyglet.gl.glScissor(self.x, self.y, self.width, self.height)

    def unset_state(self):
        pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)
