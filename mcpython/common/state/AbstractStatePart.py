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
import typing
from abc import ABC

from mcpython import shared


class AbstractStatePart(ABC):
    NAME: typing.Optional[str] = None

    def __init__(self):
        self.part_dict: typing.Dict[str, "AbstractStatePart"] = {}
        self.parts: typing.List["AbstractStatePart"] = self.get_sub_parts()
        self.master = None
        self.underlying_batch = None
        self.state_renderer = None
        self.eventbus = None

        self.state_renderer_init = False

    def init_rendering(self):
        if self.state_renderer_init:
            return
        self.state_renderer_init = True

        if not shared.IS_CLIENT:
            return

        import pyglet

        self.underlying_batch = pyglet.graphics.Batch()

        self.eventbus = self.master[-1].eventbus

        self.state_renderer = self.create_state_renderer()

        if self.state_renderer is not None:
            self.state_renderer.assigned_state = self
            self.state_renderer.batch = self.underlying_batch
            self.state_renderer.init()

            self.eventbus.subscribe(
                self.state_renderer.ASSIGNED_DRAW_STAGE, self.state_renderer.draw
            )
            self.eventbus.subscribe("user:window:resize", self.state_renderer.resize)

    def create_state_renderer(self) -> typing.Any:
        pass

    async def activate(self):
        for part in self.parts:
            await part.activate()

        if self.state_renderer is not None:
            self.state_renderer.on_activate()

    async def deactivate(self):
        for part in self.parts:
            await part.deactivate()

        if self.state_renderer is not None:
            self.state_renderer.on_deactivate()

    def get_sub_parts(self) -> typing.List["AbstractStatePart"]:
        return []

    def bind_to_eventbus(self):
        for part in self.parts:
            part.master = self.master + [self]
            part.bind_to_eventbus()
