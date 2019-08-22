"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import state.State
from state.ui import (UIPartLable, UIPartButton)
import globals as G
import pyglet
import util.math


class StateStartMenu(state.State.State):
    @staticmethod
    def get_name():
        return "minecraft:startmenu"

    def __init__(self):
        state.State.State.__init__(self)

    def get_parts(self) -> list:
        return [UIPartLable.UIPartLable("Start Menu", (0, 100), anchor_window="MM", anchor_lable="MM"),
                UIPartButton.UIPartButton((200, 15), "New Game", (0, 0), anchor_window="MM", anchor_button="MM",
                                          on_press=self.on_new_game_press)]

    @staticmethod
    def on_new_game_press(x, y):
        G.world.cleanup()
        print("generating world")
        G.worldgenerationhandler.enable_generation = True
        for x in range(-2, 3):
            for z in range(-2, 3):
                chunk = G.world.dimensions[0].get_chunk(x, z, generate=False)
                chunk.is_ready = False
                G.worldgenerationhandler.generate_chunk(chunk)
        G.world.process_entire_queue()
        G.worldgenerationhandler.enable_generation = False
        # todo: remove disable for auto-gen
        print("finished")
        G.statehandler.switch_to("minecraft:gameinfo")
        G.world.change_sectors(None, util.math.sectorize(G.window.position), immediate=True)
        G.window.position = (0, 10, 0)

    def get_event_functions(self) -> list:
        return [(self.on_draw_2d_pre, "render:draw:2d:background")]

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass

    @G.eventhandler("render:draw:2d:background", callactive=False)
    def on_draw_2d_pre(self):
        pyglet.gl.glClearColor(1., 1., 1., 1.)


startmenu = StateStartMenu()

