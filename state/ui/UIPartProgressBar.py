"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import state.StatePart
import globals as G
import pyglet.gl
import pyglet
import util.opengl


class UIPartProgressBar(state.StatePart.StatePart):
    def __init__(self, position, size, color=(1., 0., 0.), progress_items=None, status=0, text="", anchor_pgb="WS",
                 anchor_window="WS"):
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
        super().__init__()
        self.position = position
        self.size = size
        self.color = color
        self.progress_max = progress_items if progress_items is not None else size[0] - 6
        self.progress = status
        self.text = text
        self.anchor_pgb = anchor_pgb
        self.anchor_window = anchor_window

        self.lable = pyglet.text.Label(text=text)

        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)

    def _get_pgb_base_positon(self):
        x, y = self.position
        wx, wy = G.window.get_size()
        bx, by = self.size
        if self.anchor_pgb[0] == "M":
            x -= bx // 2
        elif self.anchor_pgb[0] == "E":
            x = bx - abs(x)
        if self.anchor_pgb[1] == "M":
            y -= by // 2
        elif self.anchor_pgb[1] == "N":
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

    def on_draw_2d(self):
        x, y = self._get_pgb_base_positon()
        sx, sy = self.size
        util.opengl.draw_line((x,    y),    (x,    y+sy))
        util.opengl.draw_line((x,    y),    (x+sx, y))
        util.opengl.draw_line((x+sx, y),    (x+sx, y+sy))
        util.opengl.draw_line((x,    y+sy), (x+sx, y+sy))

        sx = round(self.progress / self.progress_max * sx)
        util.opengl.draw_rectangle((x+3, y+3), (x+sx-6, y+self.size[1]-6), color=self.color)

        self.lable.text = self.text

        self.lable.x = x + (self.size[0] - self.lable.content_height) // 2
        self.lable.y = y + (self.size[1] - self.lable.content_height) // 2

