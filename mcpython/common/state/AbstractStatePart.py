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

from mcpython.util.annotation import onlyInClient


@onlyInClient()
class AbstractStatePart(ABC):
    NAME = None

    def __init__(self):
        self.part_dict = {}
        self.parts = self.get_sub_parts()
        self.master = None
        self.underlying_batch = None
        self.state_renderer = None
        self.eventbus = None

    def init_rendering(self):
        self.underlying_batch = self.master[-1].underlying_batch
        self.eventbus = self.master[-1].eventbus

        self.state_renderer = self.create_renderer()

        if self.state_renderer is not None:
            self.state_renderer.assigned_state = self
            self.state_renderer.init()

            self.eventbus.subscribe("render:draw:2d", self.state_renderer.draw)

    def create_renderer(self) -> typing.Any:
        pass

    def activate(self):
        for part in self.parts:
            part.activate()

        if self.state_renderer is not None:
            self.state_renderer.on_activate()

    def deactivate(self):
        for part in self.parts:
            part.deactivate()

        if self.state_renderer is not None:
            self.state_renderer.on_deactivate()

    def get_sub_parts(self) -> list:
        return []

    def bind_to_eventbus(self):
        for part in self.parts:
            part.master = self.master + [self]
            part.bind_to_eventbus()
