"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk"""
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
            for part in self.active_state.get_parts():
                part.deactivate()
        old = self.active_state
        self.active_state = self.states[statename]
        if statename:
            self.active_state.on_activate(old)
            for function, eventname in self.active_state.get_event_functions():
                G.eventhandler.activate_from_callback(eventname, function)
            for part in self.active_state.get_parts():
                part.activate()
            G.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())

    def add_state(self, state: State.State):
        self.states[state.get_name()] = state


handler = G.statehandler = StateHandler()


def load():
    from . import (StateGame)

    handler.switch_to("minecraft:game")

