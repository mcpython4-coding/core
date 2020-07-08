"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from . import State, StatePartGame
import mcpython.gui.InventoryHandler
import globals as G
from pyglet.window import key
import mcpython.event.TickHandler
import pyglet
from pyglet.window import mouse
import mcpython.mod.ModMcpython
import time


class StateGame(State.State):
    NAME = "minecraft:game"

    @staticmethod
    def is_mouse_exclusive(): return True

    def __init__(self): State.State.__init__(self)

    def get_parts(self) -> list:
        return [StatePartGame.StatePartGame(), mcpython.gui.InventoryHandler.inventory_part]

    def on_activate(self):
        while G.world.savefile.save_in_progress: time.sleep(0.2)
        G.worldgenerationhandler.enable_auto_gen = True

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
            if not G.world.get_active_player().inventories["main"] in G.inventoryhandler.opened_inventorystack:
                if G.window.exclusive:
                    G.eventhandler.call("on_player_inventory_open")
                    G.inventoryhandler.show(G.world.get_active_player().inventories["main"])
                    self.parts[0].activate_mouse = False
            else:
                G.eventhandler.call("on_player_inventory_close")
                G.inventoryhandler.hide(G.world.get_active_player().inventories["main"])
        elif symbol == key.T and G.window.exclusive:
            mcpython.event.TickHandler.handler.bind(self.open_chat, 2)
        elif symbol == key._7 and modifiers & key.MOD_SHIFT and G.window.exclusive:
            mcpython.event.TickHandler.handler.bind(self.open_chat, 2, args=["/"])

    @staticmethod
    def open_chat(enter=""):
        G.inventoryhandler.show(G.world.get_active_player().inventories["chat"])
        G.chat.text = enter

    @staticmethod
    def on_draw_2d_pre(): pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)


game = None


def create():
    global game
    game = StateGame()


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

