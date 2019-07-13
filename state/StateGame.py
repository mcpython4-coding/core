"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk"""
from . import State, StatePartGame


class StateGame(State.State):
    @staticmethod
    def get_name():
        return "minecraft:game"

    @staticmethod
    def is_mouse_exclusive():
        return True

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [StatePartGame.StatePartGame()]

    def get_event_functions(self) -> list:
        return []

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass


game = StateGame()

