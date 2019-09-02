"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
import gui.InventoryHandler
import globals as G
from pyglet.window import key
import chat.Chat
import json


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
        if symbol == key.ESCAPE and G.window.exclusive:
            G.statehandler.switch_to("minecraft:escape_state")
        elif symbol == key.R:
            G.inventoryhandler.reload_config()
        elif symbol == key.E:
            if not G.player.inventorys["main"] in G.inventoryhandler.opened_inventorystack:
                if G.window.exclusive:
                    G.inventoryhandler.show(G.player.inventorys["main"])
            else:
                G.inventoryhandler.hide(G.player.inventorys["main"])
        elif symbol == key.T and G.window.exclusive:
            G.inventoryhandler.show(G.player.inventorys["chat"])


game = StateGame()

