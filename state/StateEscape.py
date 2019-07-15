"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLable
import event.EventInfo
import globals as G


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
        return []

    @staticmethod
    def start_menu_press(x, y):
        G.model.cleanup()
        G.statehandler.switch_to("minecraft:startmenu")

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass


escape = StateEscape()

