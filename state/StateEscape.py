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


class StateEscape(State.State):
    @staticmethod
    def get_name():
        return "minecraft:escape_state"

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [StatePartGame.StatePartGame(activate_keyboard=False, activate_mouse=False,
                                            activate_focused_block=False, glcolor3d=(.8, .8, .8)),
                UIPartLable.UIPartLable("Game Menu", (0, 200), anchor_lable="MM", anchor_window="MM",
                                        color=(255, 255, 255, 255)),
                UIPartButton.UIPartButton((150, 25), "Back to game", (0, 150), anchor_window="MM", anchor_button="MM",
                                          on_press=event.EventInfo.CallbackHelper(
                                              G.statehandler.switch_to, ["minecraft:game"], enable_extra_args=False)),
                UIPartButton.UIPartButton((150, 25), "Back to startmenu", (0, 100), anchor_window="MM", anchor_button="MM",
                                          on_press=self.start_menu_press)
                ]

    def get_event_functions(self) -> list:
        return [(self.on_key_press, "user:keyboard:press")]

    @staticmethod
    def start_menu_press(x, y):
        G.world.cleanup()
        G.statehandler.switch_to("minecraft:startmenu")

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass

    @G.eventhandler("user:keyboard:press", callactive=False)
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:game")


escape = StateEscape()

