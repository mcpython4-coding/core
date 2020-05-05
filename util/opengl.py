"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import pyglet.gl as gl
import pyglet
import math


def draw_rectangle(position, size, color=(.0, .0, .0)):
    x, y = position
    dx, dy = size
    if len(color) == 3:
        gl.glColor3d(*color)
    else:
        gl.glColor4d(*color)
    gl.glBegin(gl.GL_TRIANGLES)
    gl.glVertex2f(x, y+dy)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x+dx, y+dy)
    gl.glVertex2f(x+dx, y+dy)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x+dx, y)
    gl.glEnd()


def draw_line(f, t, color=(.0, .0, .0)):
    gl.glColor3d(*color)
    gl.glBegin(gl.GL_LINES)
    gl.glVertex2f(*f)
    gl.glVertex2f(*t)
    gl.glEnd()


def draw_line_rectangle(position, size, color=(0., 0., 0.)):
    x, y = position
    sx, sy = size
    draw_line((x, y), (x, y + sy + 1), color=color)
    draw_line((x, y), (x + sx, y), color=color)
    draw_line((x + sx, y), (x + sx, y + sy), color=color)
    draw_line((x, y + sy), (x + sx, y + sy), color=color)

