"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import pyglet.gl as gl
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

