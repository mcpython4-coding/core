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
from abc import ABC

from mcpython.util.annotation import onlyInClient


@onlyInClient()
class AbstractStatePart(ABC):
    NAME = None

    def __init__(self):
        self.part_dict = {}
        self.parts = self.get_sub_parts()
        self.master = None

    def activate(self):
        for part in self.parts:
            part.activate()

    def deactivate(self):
        for part in self.parts:
            part.deactivate()

    def get_sub_parts(self) -> list:
        return []

    def bind_to_eventbus(self):
        for part in self.parts:
            part.master = self.master + [self]
            part.bind_to_eventbus()
