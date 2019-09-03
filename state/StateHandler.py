"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import State


class StateHandler:
    def __init__(self):
        self.active_state: State.State or None = None
        self.states = {}

    def switch_to(self, statename: str or None):
        if self.active_state:
            self.active_state.on_deactivate(self.states[statename] if statename is not None else None)
            for function, eventname in self.active_state.get_event_functions():
                G.eventhandler.deactivate_from_callback(eventname, function)
            for part in self.active_state.parts:
                part.deactivate()
        old = self.active_state
        self.active_state = self.states[statename]
        if statename:
            self.active_state.on_activate(old)
            for function, eventname in self.active_state.get_event_functions():
                G.eventhandler.activate_to_callback(eventname, function)
            for part in self.active_state.parts:
                part.activate()
            G.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())

    def add_state(self, state: State.State):
        self.states[state.get_name()] = state

    def update_exclusive(self):
        G.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())


handler = G.statehandler = StateHandler()


def load():
    from . import (StateGame, StateEscape, StateStartMenu, StateGameInfo, StateBlockItemGenerator,
                   StateWorldGenerationConfig)
    import gui.InventoryHandler

    handler.switch_to("minecraft:blockitemgenerator")

