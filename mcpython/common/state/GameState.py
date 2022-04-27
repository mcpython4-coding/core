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
import time

import mcpython.client.gui.ContainerRenderingManager
import mcpython.common.event.TickHandler
import mcpython.common.mod.ModMcpython
from mcpython import shared

from . import AbstractState, GameViewStatePart

if shared.IS_CLIENT:
    from pyglet.window import key, mouse
else:
    from mcpython.engine.rendering import key, mouse


class Game(AbstractState.AbstractState):
    NAME = "minecraft:game"

    @classmethod
    def is_mouse_exclusive(cls):
        return True

    def __init__(self):
        AbstractState.AbstractState.__init__(self)

    def create_state_parts(self) -> list:
        return [
            GameViewStatePart.GameView(clear_color=(0.5, 0.69, 1.0, 1)),
            mcpython.client.gui.ContainerRenderingManager.inventory_part,
        ]

    async def activate(self):
        await super().activate()

        if shared.IS_CLIENT:
            shared.window.mouse_pressing = {
                mouse.LEFT: False,
                mouse.RIGHT: False,
                mouse.MIDDLE: False,
            }

        while shared.world.save_file.save_in_progress:
            time.sleep(0.2)
        shared.world_generation_handler.enable_auto_gen = True

    async def deactivate(self):
        await super().deactivate()
        shared.world_generation_handler.enable_auto_gen = False

        if shared.IS_CLIENT:
            shared.window.mouse_pressing = {
                mouse.LEFT: False,
                mouse.RIGHT: False,
                mouse.MIDDLE: False,
            }

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    async def on_key_press(self, symbol, modifiers):
        if shared.state_handler.global_key_bind_toggle:
            return

        if symbol == key.ESCAPE and shared.window.exclusive:
            await shared.state_handler.change_state("minecraft:escape_menu")

        elif symbol == key.R:
            await shared.inventory_handler.reload_config()

        # todo: move impl to player
        elif symbol == key.E:
            if (
                not shared.world.get_active_player().inventory_main
                in shared.inventory_handler.open_containers
            ):
                if shared.window.exclusive:
                    await shared.event_handler.call_async("on_player_inventory_open")
                    await shared.world.get_active_player().inventory_main.reload_config()
                    await shared.inventory_handler.show(
                        shared.world.get_active_player().inventory_main
                    )
                    self.parts[0].activate_mouse = False

            else:
                await shared.event_handler.call_async("on_player_inventory_close")
                await shared.inventory_handler.hide(
                    shared.world.get_active_player().inventory_main
                )

        elif symbol == key.T and shared.window.exclusive:
            mcpython.common.event.TickHandler.handler.schedule_once(self.open_chat())

        elif symbol == key._7 and modifiers & key.MOD_SHIFT and shared.window.exclusive:
            mcpython.common.event.TickHandler.handler.bind(
                self.open_chat, 2, args=["/"]
            )

    @staticmethod
    async def open_chat(enter=""):
        await shared.inventory_handler.show(
            shared.world.get_active_player().inventory_chat
        )
        shared.chat.text = enter


game = None


async def create():
    global game
    game = Game()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create())
