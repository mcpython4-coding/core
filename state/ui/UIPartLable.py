"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import state.StatePart
import globals as G
import event.EventInfo
import pyglet
from pyglet.window import mouse
from . import UIPart
import Language


class UIPartLable(UIPart.UIPart):
    def __init__(self, text, position, press=event.EventInfo.MousePressEventInfo(pyglet.window.mouse.LEFT),
                 anchor_lable="WS", anchor_window="WS", on_press=None, color=(0, 0, 0, 255), text_size=20):
        """
        creates an new UIPartButton
        :param text: the text of the lable
        :param position: the position of the lable
        :param press: the EventInfo for mouse lables and mods, no area
        :param anchor_lable: the anchor on the lable
        :param anchor_window: the anchor on the window
        """
        super().__init__(position, 0, anchor_window=anchor_window, anchor_element=anchor_lable)
        self.text = text
        self.press: event.EventInfo.MousePressEventInfo = press
        self.color = color
        self.text_size = text_size

        self.on_press = on_press

        self.lable = pyglet.text.Label(text=text)
        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)

    def get_real_position(self):
        self.bboxsize = self.lable.content_width, self.lable.content_width
        return super().get_real_position()

    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self.get_real_position()
        sx, sy = self.lable.content_width, self.lable.content_width
        self.press.area = ((mx, my), (mx+sx, my+sy))
        if self.press.equals(x, y, button, modifiers):
            if self.on_press:
                self.on_press(x, y)

    def on_draw_2d(self):
        x, y = self.get_real_position()
        wx, wy = self.lable.content_width, self.lable.content_height
        size = self.lable.content_width, self.lable.content_width
        self.lable.x = x + size[0] // 2 - wx // 2
        self.lable.y = y + size[1] // 2 - wy // 2
        self.lable.color = self.color
        self.lable.font_size = self.text_size
        self.lable.text = Language.decode(self.text)
        self.lable.draw()

