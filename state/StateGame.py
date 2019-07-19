"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
from . import State, StatePartGame
import gui.InventoryHandler
import globals as G
from pyglet.window import key


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
        return [StatePartGame.StatePartGame(), gui.InventoryHandler.OpenedInventoryStatePart()]

    def get_event_functions(self) -> list:
        return [(self.on_key_press, "user:keyboard:press")]

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass

    @G.eventhandler("user:keyboard:press", callactive=False)
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:escape_state")
        elif symbol == key.R:
            G.inventoryhandler.reload_config()


game = StateGame()

