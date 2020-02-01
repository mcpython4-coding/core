"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import State


class StateHandler:
    def __init__(self):
        self.active_state: State.State or None = None
        self.states = {}
        self.CANCEL_SWITCH_STATE = False

    def switch_to(self, statename: str or None):
        self.CANCEL_SWITCH_STATE = False
        G.eventhandler.call("state:switch:pre", statename)
        if self.CANCEL_SWITCH_STATE: return
        if self.active_state:
            self.active_state.deactivate()
        self.active_state = self.states[statename]
        self.active_state.activate()
        G.eventhandler.call("state:switch:post", statename)

    def add_state(self, state: State.State):
        self.states[state.get_name()] = state

    def update_exclusive(self):
        G.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())


handler = G.statehandler = StateHandler()


def load():
    from . import (StateGame, StateEscape, StateStartMenu, StateGameInfo, StateBlockItemGenerator,
                   StateWorldGenerationConfig, StateModLoading)
    import gui.InventoryHandler

    handler.switch_to("minecraft:modloading")

