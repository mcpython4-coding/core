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
import sys

import pyglet
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.rendering.RenderingLayerManager import INTER_BACKGROUND

from . import AbstractState
from .ui import UIPartButton
from .util import update_memory_usage_bar


class LoadingExceptionView(AbstractState.AbstractState):
    NAME = "minecraft:loading_exception"

    def __init__(self):
        AbstractState.AbstractState.__init__(self)

        self.labels = []
        self.label_batch = pyglet.graphics.Batch()

    def set_text(self, text: str):
        for label in self.labels:
            label.delete()
        self.labels.clear()
        y = 50
        for line in reversed(text.split("\n")):
            self.labels.append(
                pyglet.text.Label(
                    text=line,
                    color=(255, 0, 100, 255),
                    anchor_x="center",
                    batch=self.label_batch,
                    y=y,
                    font_size=10,
                    x=shared.window.get_size()[0] // 2,
                )
            )
            y += 12

    def create_state_parts(self) -> list:
        from mcpython.common.state.ModLoadingProgressState import mod_loading

        return [
            mod_loading.stage_bar,
            mod_loading.memory_bar,
            UIPartButton.UIPartButton(
                (100, 20),
                "continue",
                (0, 100),
                anchor_button="MM",
                anchor_window="MN",
                on_press=self.resume,
            ),
        ]

    def resume(self, *_):
        logger.println(
            "[MOD LOADER][EXCEPTION MANAGER][INFO] continuing mod loading after forced HALT"
        )
        logger.println(
            "[MOD LOADER][EXCEPTION MANAGER][WARN] The game might be in an invalid state, errors down the road may be caused by above!"
        )

        asyncio.run(
            shared.state_handler.change_state("minecraft:mod_loading")
        )

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe(
            INTER_BACKGROUND.getRenderingEvent(), self.on_draw_2d_pre
        )
        self.eventbus.subscribe("tickhandler:general", self.on_update)

    def on_resize(self, w, h):
        for part in self.parts[:-1]:
            part.bounding_box_size = (shared.window.get_size()[0] - 40, 20)

        self.parts[1].position = (20, shared.window.get_size()[1] - 40)
        for label in self.labels:
            label.x = w // 2

    def on_draw_2d_pre(self):
        pyglet.gl.glClearColor(255, 255, 255, 255)

        update_memory_usage_bar(self.parts[1])

        self.label_batch.draw()

    def on_update(self, dt):
        pass

    async def deactivate(self):
        await super().deactivate()
        shared.world.get_active_player().init_creative_tabs()

    async def activate(self):
        await super().activate()


loading_exception = LoadingExceptionView()


def error_occur(text: str):
    if not shared.IS_CLIENT:
        print("INTERNAL ERROR OCCURRED - SCHEDULED FOR DISPLAY TO USER")
        print(text)
        sys.exit(-1)

    if shared.launch_wrapper.launch_config.setdefault("skip-loading-errors", False):
        print("INTERNAL ERROR OCCURRED - SCHEDULED FOR DISPLAY TO USER")
        print(text)
    else:
        loading_exception.set_text(text)
        shared.tick_handler.schedule_once(
            shared.state_handler.change_state(loading_exception.NAME)
        )
