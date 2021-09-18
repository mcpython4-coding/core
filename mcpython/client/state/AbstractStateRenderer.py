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

import pyglet


class AbstractStateRenderer(ABC):
    """
    Base class for state renderers
    """

    ASSIGNED_DRAW_STAGE = "render:draw:2d"

    def __init__(self):
        self.batch: typing.Optional[pyglet.graphics.Batch] = None
        self.assigned_state = None

    def init(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def draw(self):
        self.batch.draw()

    def resize(self, width: int, height: int):
        pass
