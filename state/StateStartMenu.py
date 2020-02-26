"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import state.State
from state.ui import (UIPartLable, UIPartButton, UIPartProgressBar)
import globals as G
import pyglet
import util.math
import mod.ModMcpython
import state.StatePartConfigBackground


class StateStartMenu(state.State.State):
    NAME = "minecraft:startmenu"

    def __init__(self): state.State.State.__init__(self)

    def get_parts(self) -> list:
        return [UIPartLable.UIPartLable("#*menu.game*#", (0, 100), anchor_window="MM", anchor_lable="MM",
                                        color=(255, 255, 255, 255)),
                UIPartButton.UIPartButton((200, 15), "#*menu.singleplayer*#", (0, 0), anchor_window="MM",
                                          anchor_button="MM", on_press=self.on_new_game_press),
                UIPartButton.UIPartButton((200, 15), "#*menu.quit*#", (0, -20), anchor_window="MM",
                                          anchor_button="MM", on_press=self.on_quit_game_press),
                state.StatePartConfigBackground.StatePartConfigBackground()]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    @staticmethod
    def on_new_game_press(x, y):
        G.statehandler.switch_to("minecraft:world_generation_config", immediate=False)

    @staticmethod
    def on_quit_game_press(x, y):
        G.window.close()

    @staticmethod
    def on_draw_2d_pre(): pyglet.gl.glClearColor(1., 1., 1., 1.)

    @staticmethod
    def on_key_press(key, modifier):
        if key == pyglet.window.key.ENTER:
            G.statehandler.switch_to("minecraft:world_generation_config", immediate=False)


startmenu = None


def create():
    global startmenu
    startmenu = StateStartMenu()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

