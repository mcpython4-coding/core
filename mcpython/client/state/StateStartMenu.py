"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import pyglet
import mcpython.client.state.StateWorldSelection
import mcpython.common.mod.ModMcpython
import mcpython.client.state.State


class StateStartMenu(mcpython.client.state.State.State):
    NAME = "minecraft:startmenu"
    CONFIG_LOCATION = "data/minecraft/states/start_menu.json"

    def __init__(self):
        super().__init__()

    def bind_to_eventbus(self):
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    def on_activate(self):
        G.world.world_loaded = False

    @staticmethod
    def on_new_game_press(x, y):
        G.statehandler.switch_to("minecraft:world_selection", immediate=False)

    @staticmethod
    def on_quit_game_press(x, y):
        G.window.close()

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)

    @staticmethod
    def on_key_press(key, modifier):
        if key == pyglet.window.key.ENTER:
            G.statehandler.switch_to("minecraft:world_selection", immediate=False)


startmenu = None


def create():
    global startmenu
    startmenu = StateStartMenu()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)