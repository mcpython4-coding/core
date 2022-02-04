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
import functools
import time

import mcpython.client.gui.ContainerRenderingManager
import mcpython.common.mod.ModMcpython
import mcpython.engine.event.EventInfo
import mcpython.util.callbacks
from mcpython import shared
from pyglet.window import key

from . import AbstractState, GameViewStatePart
from .ui import UIPartButton, UIPartLabel


class EscapeMenu(AbstractState.AbstractState):
    NAME = "minecraft:escape_menu"

    def __init__(self):
        AbstractState.AbstractState.__init__(self)

    def create_state_parts(self) -> list:
        return [
            GameViewStatePart.GameView(
                activate_keyboard=False,
                activate_mouse=False,
                activate_focused_block=False,
                gl_color_3d=(0.8, 0.8, 0.8),
                clear_color=(0.5, 0.69, 1.0, 1),
            ),
            UIPartLabel.UIPartLabel(
                "#*menu.game*#",
                (0, 200),
                anchor_lable="MM",
                anchor_window="MM",
                color=(255, 255, 255, 255),
            ),
            UIPartButton.UIPartButton(
                (250, 25),
                "#*menu.returnToGame*#",
                (0, 150),
                anchor_window="MM",
                anchor_button="MM",
                on_press=lambda *_: asyncio.get_event_loop().run_until_complete(
                    shared.state_handler.change_state("minecraft:game", immediate=False)
                ),
            ),
            UIPartButton.UIPartButton(
                (250, 25),
                "#*menu.returnToMenu*#",
                (0, 120),
                anchor_window="MM",
                anchor_button="MM",
                on_press=self.start_menu_press,
            ),
            UIPartButton.UIPartButton(
                (250, 25),
                "#*menu.reportBugs*#",
                (0, 90),
                anchor_window="MM",
                anchor_button="MM",
                on_press=functools.partial(mcpython.util.callbacks.open_github_project),
            ),
            mcpython.client.gui.ContainerRenderingManager.inventory_part,
        ]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    @staticmethod
    async def start_menu_press(*_):
        shared.world.world_loaded = False
        while shared.world.save_file.save_in_progress:
            time.sleep(0.2)

        if shared.IS_NETWORKING:
            await shared.NETWORK_MANAGER.disconnect()
        else:
            # make sure that file size is as small as possible
            await shared.world.save_file.save_world_async(override=True)

        shared.world.setup_by_filename("tmp")
        await shared.world.cleanup()
        await shared.event_handler.call_async("on_game_leave")
        await shared.state_handler.change_state("minecraft:start_menu", immediate=False)

        # todo: can we use an asyncio event here?
        while shared.world.save_file.save_in_progress:
            await asyncio.sleep(0.2)

    @staticmethod
    async def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            await shared.state_handler.change_state("minecraft:game", immediate=False)

    async def activate(self):
        await super().activate()

        if not shared.IS_NETWORKING:
            shared.tick_handler.schedule_once(shared.world.save_file.save_world_async)


escape = None


async def create():
    global escape
    escape = EscapeMenu()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create())
