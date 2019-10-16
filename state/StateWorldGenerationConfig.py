"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLable
import globals as G
import util.math
from pyglet.window import key
import pyglet


class StateWorldGenerationConfig(State.State):
    @staticmethod
    def get_name(): return "minecraft:world_generation_config"

    def __init__(self): State.State.__init__(self)

    def get_parts(self) -> list:
        return [UIPartButton.UIPartButton((200, 20), "BACK", (-220, 20), anchor_window="MD",
                                          on_press=self.on_back_press),
                UIPartButton.UIPartButton((200, 20), "GENERATE", (20, 20), anchor_window="MD",
                                          on_press=self.on_generate_press)]

    def on_back_press(self, x, y):
        G.statehandler.switch_to("minecraft:startmenu")

    def on_generate_press(self, x, y):
        G.world.cleanup(remove_dims=True)
        G.world.add_dimension(0, {"configname": "default_overworld"})
        area = [-1, 2, -1, 2]
        G.worldgenerationhandler.enable_generation = True
        for cx in range(*area[:2]):
            for cz in range(*area[2:]):
                chunk = G.world.dimensions[0].get_chunk(cx, cz, generate=False)
                chunk.is_ready = False
                G.worldgenerationhandler.generate_chunk(chunk)
                chunk.is_ready = True
        G.window.position = (0, util.math.get_max_y((0, 0, 0)), 0)
        G.world.config["enable_auto_gen"] = True
        G.world.config["enable_world_barrier"] = True
        G.statehandler.switch_to("minecraft:gameinfo")

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_back_press(0, 0)

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(1., 1., 1., 1.)


escape = StateWorldGenerationConfig()

