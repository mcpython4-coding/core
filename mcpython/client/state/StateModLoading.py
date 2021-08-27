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
from mcpython.util.annotation import onlyInClient

from . import State
from .ui import UIPartProgressBar
from .util import update_memory_usage_bar


@onlyInClient()
class StateModLoading(State.State):
    NAME = "minecraft:mod_loading"

    def __init__(self):
        self.stage_bar = None
        self.mod_bar = None
        self.item_bar = None
        self.memory_bar = None

        super().__init__()

    def get_parts(self) -> list:
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
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_resize(self, w, h):
        for part in self.parts:
            part.bounding_box_size = (shared.window.get_size()[0] - 40, 20)

        self.parts[3].position = (20, shared.window.get_size()[1] - 40)

    def on_draw_2d_pre(self):
        pyglet.gl.glClearColor(255, 255, 255, 255)

        update_memory_usage_bar(self.memory_bar)

    def on_update(self, dt):
        shared.mod_loader.process()

    def deactivate(self):
        super().deactivate()
        shared.world.get_active_player().init_creative_tabs()


mod_loading = StateModLoading()
