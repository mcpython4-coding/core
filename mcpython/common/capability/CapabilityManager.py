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

from .AbstractCapability import AbstractCapability
from mcpython import shared


class CapabilityManager:
    def __init__(self):
        self.capabilities: typing.Dict[str, AbstractCapability] = {}

    def get_by_name(self, name: str) -> AbstractCapability:
        return self.capabilities[name]

    def register(self, name: str, capability: AbstractCapability):
        self.capabilities[name] = capability
        return capability


shared.capability_manager = CapabilityManager()

