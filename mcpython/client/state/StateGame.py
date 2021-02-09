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
from . import State, StatePartGame
import mcpython.client.gui.InventoryHandler
from mcpython import shared
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
        while shared.world.save_file.save_in_progress:
            time.sleep(0.2)
        shared.world_generation_handler.enable_auto_gen = True

    def deactivate(self):
        super().deactivate()
        shared.world_generation_handler.enable_auto_gen = False
        shared.window.mouse_pressing = {
            mouse.LEFT: False,
            mouse.RIGHT: False,
            mouse.MIDDLE: False,
        }

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE and shared.window.exclusive:
            shared.state_handler.switch_to("minecraft:escape_state")
        elif symbol == key.R:
            shared.inventory_handler.reload_config()
        elif symbol == key.E:
            if (
                not shared.world.get_active_player().inventory_main
                in shared.inventory_handler.opened_inventory_stack
            ):
                if shared.window.exclusive:
                    shared.event_handler.call("on_player_inventory_open")
                    shared.inventory_handler.show(
                        shared.world.get_active_player().inventory_main
                    )
                    self.parts[0].activate_mouse = False
            else:
                shared.event_handler.call("on_player_inventory_close")
                shared.inventory_handler.hide(
                    shared.world.get_active_player().inventory_main
                )
        elif symbol == key.T and shared.window.exclusive:
            mcpython.common.event.TickHandler.handler.bind(self.open_chat, 2)
        elif symbol == key._7 and modifiers & key.MOD_SHIFT and shared.window.exclusive:
            mcpython.common.event.TickHandler.handler.bind(
                self.open_chat, 2, args=["/"]
            )

    @staticmethod
    def open_chat(enter=""):
        shared.inventory_handler.show(shared.world.get_active_player().inventory_chat)
        shared.chat.text = enter

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)


game = None


@onlyInClient()
def create():
    global game
    game = StateGame()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
