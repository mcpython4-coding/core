"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
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
from pyglet.window import mouse
import mod.ModMcpython


class StateGame(State.State):
    @staticmethod
    def get_name(): return "minecraft:game"

    @staticmethod
    def is_mouse_exclusive(): return True

    def __init__(self): State.State.__init__(self)

    def get_parts(self) -> list:
        return [StatePartGame.StatePartGame(), gui.InventoryHandler.inventory_part]

    def on_activate(self): G.worldgenerationhandler.enable_auto_gen = True

    def on_deactivate(self):
        G.worldgenerationhandler.enable_auto_gen = False
        G.window.mouse_pressing = {mouse.LEFT: False, mouse.RIGHT: False, mouse.MIDDLE: False}

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE and G.window.exclusive:
            G.statehandler.switch_to("minecraft:escape_state")
        elif symbol == key.R:
            G.inventoryhandler.reload_config()
        elif symbol == key.E:
            if not G.player.inventorys["main"] in G.inventoryhandler.opened_inventorystack:
                if G.window.exclusive:
                    G.eventhandler.call("on_player_inventory_open")
                    G.inventoryhandler.show(G.player.inventorys["main"])
            else:
                G.eventhandler.call("on_player_inventory_close")
                G.inventoryhandler.hide(G.player.inventorys["main"])
        elif symbol == key.T and G.window.exclusive:
            event.TickHandler.handler.bind(self.open_chat, 2)
        elif symbol == key._7 and modifiers & key.MOD_SHIFT and G.window.exclusive:
            event.TickHandler.handler.bind(self.open_chat, 2, args=["/"])

    @staticmethod
    def open_chat(enter=""):
        G.inventoryhandler.show(G.player.inventorys["chat"])
        G.chat.text = enter

    @staticmethod
    def on_draw_2d_pre(): pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)


game = None


def create():
    global game
    game = StateGame()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

