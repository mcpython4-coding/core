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
import asyncio

import mcpython.common.mod.ModMcpython
import mcpython.common.state.AbstractState
import pyglet
from mcpython import shared
from mcpython.util.annotation import onlyInClient


class StartMenu(mcpython.common.state.AbstractState.AbstractState):
    NAME = "minecraft:start_menu"
    CONFIG_LOCATION = "data/minecraft/states/start_menu.json"

    def __init__(self):
        super().__init__()

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    async def activate(self):
        await super().activate()
        shared.world.world_loaded = False
        shared.ENABLE_ANIMATED_TEXTURES = True

    @staticmethod
    def on_new_game_press(x, y):
        asyncio.get_event_loop().run_until_complete(shared.state_handler.change_state("minecraft:world_selection", immediate=False))

    @staticmethod
    def on_quit_game_press(x, y):
        shared.window.close()

    @staticmethod
    def on_key_press(key, modifier):
        if key == pyglet.window.key.ENTER:
            asyncio.get_event_loop().run_until_complete(shared.state_handler.change_state(
                "minecraft:world_selection", immediate=False
            ))

    @staticmethod
    def on_multiplayer_press(x, y):
        asyncio.get_event_loop().run_until_complete(shared.state_handler.change_state("minecraft:server_selection"))


start_menu = None


async def create():
    global start_menu
    start_menu = StartMenu()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create())
