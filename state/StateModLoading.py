"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
from .ui import UIPartProgressBar
import event.EventInfo
import globals as G
import pyglet
import util.opengl


class StateModLoading(State.State):
    @staticmethod
    def get_name():
        return "minecraft:modloading"

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [UIPartProgressBar.UIPartProgressBar((10, 10), (20, 20), status=1)]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_resize(self, w, h):
        self.parts[0].size = (w-80, 20)

    def on_draw_2d_pre(self):
        pyglet.gl.glClearColor(255, 255, 255, 255)
        self.parts[0].bboxsize = (G.window.get_size()[0]-40, 20)

    def on_update(self, dt):
        G.modloader.process()

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass


modloading = StateModLoading()
