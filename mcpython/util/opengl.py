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
import math

import pyglet

# This is an semi-stable API for drawing stuff on the screen.
# todo: implement via pyglet's shape module & use batches
# todo: use geometry shaders after pyglet 2.0
import pyglet.gl as gl


def draw_rectangle(position, size, color=(0.0, 0.0, 0.0)):
    x, y = position
    dx, dy = size
    if len(color) == 3:
        gl.glColor3d(*color)
    else:
        gl.glColor4d(*color)
    gl.glBegin(gl.GL_TRIANGLES)
    gl.glVertex2f(x, y + dy)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x + dx, y + dy)
    gl.glVertex2f(x + dx, y + dy)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x + dx, y)
    gl.glEnd()
    gl.glColor3d(1, 1, 1)


def draw_line(f, t, color=(0.0, 0.0, 0.0)):
    gl.glColor3d(*color)
    gl.glBegin(gl.GL_LINES)
    gl.glVertex2f(*f)
    gl.glVertex2f(*t)
    gl.glEnd()
    gl.glColor3d(1, 1, 1)


def draw_line_rectangle(position, size, color=(0.0, 0.0, 0.0)):
    x, y = position
    sx, sy = size
    draw_line((x, y), (x, y + sy + 1), color=color)
    draw_line((x, y), (x + sx, y), color=color)
    draw_line((x + sx, y), (x + sx, y + sy), color=color)
    draw_line((x, y + sy), (x + sx, y + sy), color=color)
    gl.glColor3d(1, 1, 1)
