"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLable
import event.EventInfo
import globals as G
from pyglet.window import key
import pyglet
import state.StateGame
import util.callbacks
import mod.ModMcpython


class StateEscape(State.State):
    @staticmethod
    def get_name():
        return "minecraft:escape_state"

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

    def get_event_functions(self) -> list:
        return [(self.on_key_press, "user:keyboard:press"),
                (self.on_draw_2d_pre, "render:draw:2d:background")]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    @staticmethod
    def start_menu_press(x, y):
        G.world.cleanup()
        G.eventhandler.call("on_game_leave")
        G.statehandler.switch_to("minecraft:startmenu")

    @staticmethod
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:game")

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)


escape = None


def create():
    global escape
    escape = StateEscape()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

