"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.state.AbstractState
import mcpython.common.mod.ModMcpython
import pyglet
from mcpython import shared
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StartMenu(mcpython.common.state.AbstractState.AbstractState):
    NAME = "minecraft:start_menu"
    CONFIG_LOCATION = "data/minecraft/states/start_menu.json"

    def __init__(self):
        super().__init__()

    def bind_to_eventbus(self):
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    def activate(self):
        super().activate()
        shared.world.world_loaded = False

    @staticmethod
    def on_new_game_press(x, y):
        shared.state_handler.change_state("minecraft:world_selection", immediate=False)

    @staticmethod
    def on_quit_game_press(x, y):
        shared.window.close()

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)

    @staticmethod
    def on_key_press(key, modifier):
        if key == pyglet.window.key.ENTER:
            shared.state_handler.change_state(
                "minecraft:world_selection", immediate=False
            )

    @staticmethod
    def on_multiplayer_press(x, y):
        shared.state_handler.change_state("minecraft:server_selection")


start_menu = None


@onlyInClient()
def create():
    global start_menu
    start_menu = StartMenu()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
