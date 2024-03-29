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
import psutil
import pyglet
from mcpython import shared
from mcpython.engine.rendering.RenderingLayerManager import INTER_BACKGROUND

from . import AbstractState
from .ui import UIPartProgressBar
from .util import update_memory_usage_bar


class ModLoadingProgress(AbstractState.AbstractState):
    NAME = "minecraft:mod_loading"

    def __init__(self):
        self.stage_bar = None
        self.mod_bar = None
        self.item_bar = None
        self.memory_bar = None

        super().__init__()

    def create_state_parts(self) -> list:
        self.stage_bar = UIPartProgressBar.UIPartProgressBar(
            (20, 10), (20, 20), status=1, color=(1.0, 0.0, 0.0)
        )
        self.mod_bar = UIPartProgressBar.UIPartProgressBar(
            (20, 40), (20, 20), status=1, color=(0.0, 0.0, 1.0)
        )
        self.item_bar = UIPartProgressBar.UIPartProgressBar(
            (20, 70), (20, 20), status=1, color=(0.0, 1.0, 0.0)
        )
        self.memory_bar = UIPartProgressBar.UIPartProgressBar(
            (20, 10),
            (20, 20),
            status=1,
            color=(1.0, 0.0, 0.0),
            progress_items=psutil.virtual_memory().total,
        )

        return [
            self.stage_bar,
            self.mod_bar,
            self.item_bar,
            self.memory_bar,
        ]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe(
            INTER_BACKGROUND.getRenderingEvent(), self.on_draw_2d_pre
        )
        self.eventbus.subscribe("tickhandler:general", self.on_update)

    def on_resize(self, w, h):
        for part in self.parts:
            part.bounding_box_size = (shared.window.get_size()[0] - 40, 20)

        self.parts[3].position = (20, shared.window.get_size()[1] - 40)

    def on_draw_2d_pre(self):
        pyglet.gl.glClearColor(255, 255, 255, 255)

        update_memory_usage_bar(self.memory_bar)

    async def on_update(self, dt):
        await shared.mod_loader.process()

    async def deactivate(self):
        await super().deactivate()

        if shared.IS_CLIENT:
            (await shared.world.get_active_player_async()).init_creative_tabs()


mod_loading = ModLoadingProgress()
