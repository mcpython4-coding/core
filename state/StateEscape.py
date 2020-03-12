"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLable
import event.EventInfo
import globals as G
from pyglet.window import key
import pyglet
import state.StateGame
import util.callbacks
import mod.ModMcpython
import time


class StateEscape(State.State):
    NAME = "minecraft:escape_state"

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [StatePartGame.StatePartGame(activate_keyboard=False, activate_mouse=False,
                                            activate_focused_block=False, glcolor3d=(.8, .8, .8)),
                UIPartLable.UIPartLable("#*menu.game*#", (0, 200), anchor_lable="MM", anchor_window="MM",
                                        color=(255, 255, 255, 255)),
                UIPartButton.UIPartButton((250, 25), "#*menu.returnToGame*#", (0, 150), anchor_window="MM",
                                          anchor_button="MM", on_press=event.EventInfo.CallbackHelper(
                        G.statehandler.switch_to, ["minecraft:game"], enable_extra_args=False)),
                UIPartButton.UIPartButton((250, 25), "#*menu.returnToMenu*#", (0, 120), anchor_window="MM",
                                          anchor_button="MM", on_press=self.start_menu_press),
                UIPartButton.UIPartButton((250, 25), "#*menu.reportBugs*#", (0, 90), anchor_window="MM",
                                          anchor_button="MM", on_press=event.EventInfo.CallbackHelper(
                        util.callbacks.open_github_project, enable_extra_args=False)),
                state.StateGame.game.parts[1]]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    @staticmethod
    def start_menu_press(x, y):
        while G.world.savefile.save_in_progress: time.sleep(0.2)
        G.world.savefile.save_world(override=True)  # make sure that file size is as small as possible
        G.world.setup_by_filename("tmp")
        G.world.cleanup()
        G.eventhandler.call("on_game_leave")
        G.statehandler.switch_to("minecraft:startmenu", immediate=False)
        while G.world.savefile.save_in_progress: time.sleep(0.2)

    @staticmethod
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:game", immediate=False)

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)

    def on_activate(self):
        pyglet.clock.schedule_once(G.world.savefile.save_world, 0.1)


escape = None


def create():
    global escape
    escape = StateEscape()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

