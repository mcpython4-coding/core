"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from pyglet.gl import *
import pyglet
import mcpython.common.config
from mcpython.util.annotation import onlyInClient


__all__ = ["setup", "setup_fog", "draw_line_box", "set_2d", "set_3d"]


@onlyInClient()
def setup():
    # Enable culling (not rendering) of back-facing facets -- facets that aren't visible to you
    # todo: move to world rendering code and disable when drawing with alpha
    glEnable(GL_CULL_FACE)

    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    # setup system for alpha drawing
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    pyglet.image.Texture.default_min_filter = GL_NEAREST
    pyglet.image.Texture.default_mag_filter = GL_NEAREST

    setup_fog()


@onlyInClient()
def setup_fog():
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)

    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (pyglet.gl.GLfloat * 4)(0.5, 0.69, 1.0, 1))

    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)

    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)

    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, mcpython.common.config.FOG_DISTANCE)
    glFogf(GL_FOG_END, 40.0 + mcpython.common.config.FOG_DISTANCE)


@onlyInClient()
def draw_line_box(vertex):
    glColor3d(0, 0, 0)
    glLineWidth(1.3)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    pyglet.graphics.draw(24, GL_QUADS, vertex)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glLineWidth(1)


@onlyInClient()
def set_2d(viewport, width, height):
    glDisable(GL_DEPTH_TEST)
    glViewport(0, 0, viewport[0], viewport[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


@onlyInClient()
def set_3d(viewport, width, height, rotation, trans_rotation, position):
    glEnable(GL_DEPTH_TEST)
    glViewport(0, 0, viewport[0], viewport[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # calculate far with rendering distance
    gluPerspective(65.0, width / height, 0.1, mcpython.common.config.FOG_DISTANCE + 20)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotated(rotation[0], 0, 1, 0)
    glRotated(rotation[1], trans_rotation[0], 0, trans_rotation[1])
    glTranslated(-position[0], -position[1], -position[2])
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


@onlyInClient()
def enableAlpha():
    glDisable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


@onlyInClient()
def disableAlpha():
    glBlendFunc(GL_ONE, GL_ZERO)
    glEnable(GL_CULL_FACE)
