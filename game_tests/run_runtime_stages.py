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
import importlib

# todo: somehow, disable user input (and bind ESC to close the window?)
import json
import os

local = os.path.dirname(__file__)
index_file = local + "/runtime/index.json"

with open(index_file, mode="r") as f:
    index = json.load(f)


import game_tests.runtime.api.Stages
import mcpython.engine.event.EventHandler
from mcpython import shared


async def prepare():
    from mcpython.common.data import ResourcePipe
    from mcpython.common.state.WorldGenerationProgressState import spawn_empty_world

    await ResourcePipe.handler.reload_content()

    await shared.world.cleanup()
    await spawn_empty_world()

    await shared.state_handler.change_state("minecraft:game")

    player = await shared.world.get_active_player_async()

    # Create the inventories needed
    await player.create_inventories()

    assert player.name == "unknown"

    player.set_gamemode(3)
    player.flying = True
    player.position = 0, 0, 0

    window = shared.window
    window.set_fullscreen(False)
    window.set_size(800, 600)
    window.set_minimum_size(800, 600)
    window.set_maximum_size(800, 600)
    window.set_size(800, 600)

    shared.tick_handler.schedule_once(game_tests.runtime.api.Stages.MANAGER.auto_run())


async def cancel_start_menu(handle):
    shared.tick_handler.schedule_once(prepare())
    handle.cancel()


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "stage_handler:loading2main_menu", cancel_start_menu
)


for module in index:
    importlib.import_module("game_tests.runtime." + module)


asyncio.run(game_tests.runtime.api.Stages.init_tests())

import mcpython.LaunchWrapper

launch = mcpython.LaunchWrapper.LaunchWrapper()

if __name__ == "__main__":
    launch.full_launch()
