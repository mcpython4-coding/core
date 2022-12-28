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
import mcpython.util.opengl
import pyglet
import pyglet.gl
from mcpython.engine.rendering.RenderingLayerManager import MIDDLE_GROUND

from . import AbstractUIPart


class UIPartProgressBar(AbstractUIPart.AbstractUIPart):
    def __init__(
        self,
        position,
        size,
        color=(1.0, 0.0, 0.0, 1.0),
        progress_items=None,
        status=0,
        text="",
        anchor_pgb="WS",
        anchor_window="WS",
        text_color=(0, 0, 0, 255),
    ):
        """
        creates an new UIPartProgressBar
        :param position: the position to create on
        :param size: the size of the progressbar
        :param color: the color to use for the progress
        :param progress_items: the amount of items that the progressbar holds. default: size[0]-6
        :param status: how far we are at the moment
        :param text: the text to draw ontop of the progress bar
        :param anchor_pgb: the anchor on the progress bar
        :param anchor_window: the anchor on the window
        """
        assert len(color) == 4

        super().__init__(
            position, size, anchor_element=anchor_pgb, anchor_window=anchor_window
        )
        self.color = color
        self.progress_max = (
            progress_items if progress_items is not None else size[0] - 6
        )
        self.progress = status
        self.text = text

        self.lable = pyglet.text.Label(
            text=text, color=text_color, font_size=size[1] - 10
        )

        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe(
            MIDDLE_GROUND.getRenderingEvent(), self.on_draw_2d
        )

    def on_draw_2d(self):
        x, y = self.get_real_position()
        mcpython.util.opengl.draw_line_rectangle((x, y), self.bounding_box_size)
        sx, sy = self.bounding_box_size

        if self.progress > self.progress_max:
            self.progress = self.progress_max

        sx = (
            (sx - 5)
            * self.progress
            // (self.progress_max if self.progress_max != 0 else 1)
        )
        mcpython.util.opengl.draw_rectangle(
            (x + 2, y + 3), (sx, self.bounding_box_size[1] - 5), color=self.color
        )

        self.lable.text = self.text

        self.lable.font_size = self.bounding_box_size[1] - 10
        while self.lable.content_width > self.bounding_box_size[0]:
            self.lable.font_size -= 1

        self.lable.x = x + (self.bounding_box_size[0] - self.lable.content_width) // 2
        self.lable.y = (
            y + (self.bounding_box_size[1] - self.lable.content_height) // 2 + 5
        )

        self.lable.draw()
