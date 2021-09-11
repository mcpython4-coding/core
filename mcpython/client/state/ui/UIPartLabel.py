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
import mcpython.common.data.Language
import mcpython.engine.event.EventInfo
import pyglet
from mcpython.util.annotation import onlyInClient
from pyglet.window import mouse

from . import AbstractUIPart


@onlyInClient()
class UIPartLabel(AbstractUIPart.AbstractUIPart):
    def __init__(
        self,
        text,
        position,
        press=mcpython.engine.event.EventInfo.MousePressEventInfo(
            pyglet.window.mouse.LEFT
        ),
        anchor_lable="WS",
        anchor_window="WS",
        on_press=None,
        color=(0, 0, 0, 255),
        text_size=20,
        text_color=(0, 0, 0, 255),
    ):
        """
        Creates a new label
        :param text: the text of the label
        :param position: the position of the label
        :param press: the EventInfo for mouse labels and mods, no area
        :param anchor_label: the anchor on the label
        :param anchor_window: the anchor on the window
        :param on_press: called when the mouse presses on the label together with x and y
        :param color: the color of the text to use
        :param text_size: the size of the text
        """
        super().__init__(
            position, 0, anchor_window=anchor_window, anchor_element=anchor_lable
        )
        if len(color) != 4:
            raise ValueError("color must be an tuple of (r, g, b, a)")
        self.text = text
        self.press: mcpython.engine.event.EventInfo.MousePressEventInfo = press
        self.color = color
        self.text_size = text_size
        self.text_color = text_color

        self.on_press = on_press

        self.lable = pyglet.text.Label(text=text, color=text_color)
        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)

    def get_real_position(self):
        self.bounding_box_size = self.lable.content_width, self.lable.content_width
        return super().get_real_position()

    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self.get_real_position()
        sx, sy = self.lable.content_width, self.lable.content_width
        self.press.area = ((mx, my), (mx + sx, my + sy))
        if self.press.equals(x, y, button, modifiers):
            if self.on_press:
                self.on_press(x, y)

    def on_draw_2d(self):
        x, y = self.get_real_position()
        wx, wy = self.lable.content_width, self.lable.content_height
        size = self.lable.content_width, self.lable.content_width
        # todo: check for change in window size
        self.lable.x = x + size[0] // 2 - wx // 2
        self.lable.y = y + size[1] // 2 - wy // 2
        self.lable.color = self.color
        self.lable.font_size = self.text_size
        self.lable.text = mcpython.common.data.Language.translate(self.text)
        self.lable.color = self.text_color
        self.lable.draw()
