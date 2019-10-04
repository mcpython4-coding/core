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
import event.TickHandler
import pyglet


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
        return [(self.on_key_press, "user:keyboard:press"),
                (self.on_draw_2d_pre, "render:draw:2d:background")]

    def on_activate(self, old):
        G.worldgenerationhandler.enable_auto_gen = True

    def on_deactivate(self, new):
        G.worldgenerationhandler.enable_auto_gen = False

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
            event.TickHandler.handler.bind(self.open_chat, 2)
        elif symbol == key._7 and modifiers & key.MOD_SHIFT:
            event.TickHandler.handler.bind(self.open_chat, 2, args=["/"])

    @staticmethod
    def open_chat(enter=""):
        G.inventoryhandler.show(G.player.inventorys["chat"])
        G.chat.text = enter

    @G.eventhandler("render:draw:2d:background", callactive=False)
    def on_draw_2d_pre(self):
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)


game = StateGame()

