"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State, StatePartGame
from .ui import UIPartProgressBar
import event.EventInfo
import globals as G
import pyglet
import util.opengl
import psutil


class StateModLoading(State.State):
    NAME = "minecraft:modloading"

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [UIPartProgressBar.UIPartProgressBar((10, 10), (20, 20), status=1, color=(1., 0., 0.)),  # stage
                UIPartProgressBar.UIPartProgressBar((10, 40), (20, 20), status=1, color=(0., 0., 1.)),  # mod
                UIPartProgressBar.UIPartProgressBar((10, 70), (20, 20), status=1, color=(0., 1., 0.)),  # item
                UIPartProgressBar.UIPartProgressBar((10, 10), (20, 20), status=1,  # memory usage
                                                    color=(1., 0., 0.), progress_items=psutil.virtual_memory().total)]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_resize(self, w, h):
        for part in self.parts:
            part.bboxsize = (w, h)

    def on_draw_2d_pre(self):
        pyglet.gl.glClearColor(255, 255, 255, 255)
        for part in self.parts:
            part.bboxsize = (G.window.get_size()[0]-40, 20)
        self.parts[3].position = (10, G.window.get_size()[1]-40)
        process = psutil.Process()
        with process.oneshot():
            self.parts[3].progress = process.memory_info().rss
        self.parts[3].text = "Memory usage: {}MB/{}MB ({}%)".format(
            self.parts[3].progress//2 ** 20, self.parts[3].progress_max//2 ** 20,
            round(self.parts[3].progress/self.parts[3].progress_max*10000)/100)

    def on_update(self, dt):
        G.modloader.process()


modloading = StateModLoading()
