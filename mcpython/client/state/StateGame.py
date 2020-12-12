"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from . import State, StatePartGame
import mcpython.client.gui.InventoryHandler
from mcpython import shared as G
from pyglet.window import key
import mcpython.common.event.TickHandler
import pyglet
from pyglet.window import mouse
import mcpython.common.mod.ModMcpython
import time
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StateGame(State.State):
    NAME = "minecraft:game"

    @classmethod
    def is_mouse_exclusive(cls):
        return True

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [
            StatePartGame.StatePartGame(),
            mcpython.client.gui.InventoryHandler.inventory_part,
        ]

    def activate(self):
        super().activate()
        while G.world.savefile.save_in_progress:
            time.sleep(0.2)
        G.world_generation_handler.enable_auto_gen = True

    def deactivate(self):
        super().deactivate()
        G.world_generation_handler.enable_auto_gen = False
        G.window.mouse_pressing = {
            mouse.LEFT: False,
            mouse.RIGHT: False,
            mouse.MIDDLE: False,
        }

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE and G.window.exclusive:
            G.state_handler.switch_to("minecraft:escape_state")
        elif symbol == key.R:
            G.inventory_handler.reload_config()
        elif symbol == key.E:
            if (
                not G.world.get_active_player().inventory_main
                in G.inventory_handler.opened_inventorystack
            ):
                if G.window.exclusive:
                    G.event_handler.call("on_player_inventory_open")
                    G.inventory_handler.show(
                        G.world.get_active_player().inventory_main
                    )
                    self.parts[0].activate_mouse = False
            else:
                G.event_handler.call("on_player_inventory_close")
                G.inventory_handler.hide(G.world.get_active_player().inventory_main)
        elif symbol == key.T and G.window.exclusive:
            mcpython.common.event.TickHandler.handler.bind(self.open_chat, 2)
        elif symbol == key._7 and modifiers & key.MOD_SHIFT and G.window.exclusive:
            mcpython.common.event.TickHandler.handler.bind(
                self.open_chat, 2, args=["/"]
            )

    @staticmethod
    def open_chat(enter=""):
        G.inventory_handler.show(G.world.get_active_player().inventory_chat)
        G.chat.text = enter

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)


game = None


@onlyInClient()
def create():
    global game
    game = StateGame()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
