"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import pyglet.gl as gl
import pyglet
import math


def draw_rectangle(position, size, color=(.0, .0, .0)):
    x, y = position
    dx, dy = size
    gl.glColor3d(*color)
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

