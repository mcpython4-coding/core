"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import state.StatePart
import globals as G
import event.EventInfo
import pyglet
from pyglet.window import mouse


class UIPartLable(state.StatePart.StatePart):
    def __init__(self, image: pyglet.sprite.Sprite, position, anchor_window="WS", on_press=None,
                 press=event.EventInfo.MousePressEventInfo(pyglet.window.mouse.LEFT), anchor_lable="WS"):
        """
        creates an new UIPartButton
        :param position: the position of the button
        :param press: the EventInfo for mouse buttons and mods, no area
        :param anchor_lable: the anchor on the button
        :param anchor_window: the anchor on the window
        """
        self.image = image
        self.position = position
        self.press: event.EventInfo.MousePressEventInfo = press
        self.anchor_lable = anchor_lable
        self.anchor_window = anchor_window

        self.on_press = on_press

        self.event_functions = [("user:mouse:press", self.on_mouse_press),
                                ("render:draw:2d", self.on_draw_2d)]

    def activate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.activate_to_callback(eventname, function)

    def deactivate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.deactivate_from_callback(eventname, function)

    def _get_button_base_positon(self):
        x, y = self.position
        wx, wy = G.window.get_size()
        bx, by = self.image.image.width, self.image.image.height
        if self.anchor_lable[0] == "M":
            x -= bx // 2
        elif self.anchor_lable[0] == "E":
            x = bx - abs(x)
        if self.anchor_lable[1] == "M":
            y -= by // 2
        elif self.anchor_lable[1] == "N":
            y = by - abs(y)
        if self.anchor_window[0] == "M":
            x += wx // 2
        elif self.anchor_window[0] == "E":
            x = wx - abs(x)
        if self.anchor_window[1] == "M":
            y += wy // 2
        elif self.anchor_window[1] == "N":
            y = wy - abs(y)
        return x, y

    @G.eventhandler("user:mouse:press", callactive=False)
    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self._get_button_base_positon()
        sx, sy = self.image.image.width, self.image.image.height
        self.press.area = ((mx, my), (mx+sx, my+sy))
        if self.press.equals(x, y, button, modifiers):
            if self.on_press:
                self.on_press(x, y)

    @G.eventhandler("render:draw:2d", callactive=False)
    def on_draw_2d(self):
        x, y = self._get_button_base_positon()
        wx, wy = size = self.image.image.width, self.image.image.height
        self.image.position = (x + size[0] // 2 - wx // 2, y + size[1] // 2 - wy // 2)
        self.image.draw()

