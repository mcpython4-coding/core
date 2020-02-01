"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import state.StatePart
import globals as G
import event.EventInfo
import pyglet
from pyglet.window import mouse
from . import UIPart


class UIPartImage(UIPart.UIPart):
    def __init__(self, image: pyglet.sprite.Sprite, position, anchor_window="WS", on_press=None,
                 press=event.EventInfo.MousePressEventInfo(pyglet.window.mouse.LEFT), anchor_image="WS"):
        """
        creates an new UIPartButton
        :param position: the position of the button
        :param press: the EventInfo for mouse buttons and mods, no area
        :param anchor_image: the anchor on the button
        :param anchor_window: the anchor on the window
        """
        super().__init__(position, (image.width, image.height), anchor_element=anchor_image,
                         anchor_window=anchor_window)
        self.image = image
        self.press: event.EventInfo.MousePressEventInfo = press

        self.on_press = on_press
        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)

    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self.get_real_position()
        sx, sy = self.image.image.width, self.image.image.height
        self.press.area = ((mx, my), (mx+sx, my+sy))
        if self.press.equals(x, y, button, modifiers):
            if self.on_press:
                self.on_press(x, y)

    def on_draw_2d(self):
        x, y = self.get_real_position()
        wx, wy = size = self.image.image.width, self.image.image.height
        self.image.position = (x + size[0] // 2 - wx // 2, y + size[1] // 2 - wy // 2)
        self.image.draw()

