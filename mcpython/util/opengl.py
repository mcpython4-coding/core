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

import deprecation
import pyglet

try:
    # This is an semi-stable API for drawing stuff on the screen.
    # todo: implement via pyglet's shape module & use batches
    # todo: use geometry shaders after pyglet 2.0
    import pyglet.gl as gl
except ImportError:
    gl = None


@deprecation.deprecated(details="Use pyglet's shapes module!")
def draw_rectangle(position, size, color=(0.0, 0.0, 0.0, 1.0)):
    assert len(color) == 4

    x, y = position
    dx, dy = size

    pyglet.graphics.draw(
        6,
        gl.GL_TRIANGLES,
        colors=("f", color * 6),
        position=(
            "f",
            (
                x, y + dy, 0,
                x, y, 0,
                x + dx, y + dy, 0,
                x + dx, y + dy, 0,
                x, y, 0,
                x + dx, y, 0,
            )
        )
    )


@deprecation.deprecated(details="Use pyglet's shapes module!")
def draw_line(f, t, color=(0.0, 0.0, 0.0, 1.0)):
    assert len(color) == 4
    pyglet.graphics.draw(2, gl.GL_LINES, colors=("f", color*2), position=("f", f+(0,)+t+(0,)))


@deprecation.deprecated(details="Use pyglet's shapes module!")
def draw_line_rectangle(position, size, color=(0.0, 0.0, 0.0, 1.0)):
    assert len(color) == 4
    x, y = position
    sx, sy = size
    draw_line((x, y), (x, y + sy + 1), color=color)
    draw_line((x, y), (x + sx, y), color=color)
    draw_line((x + sx, y), (x + sx, y + sy), color=color)
    draw_line((x, y + sy), (x + sx, y + sy), color=color)
