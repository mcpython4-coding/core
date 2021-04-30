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


class AbstractMap(ABC):
    """
    Abstract map class holding information about a Chunk, in map-like formats
    Contains code for writing to saves, by default, does nothing
    """

    NAME = None

    @classmethod
    def init_on(cls, chunk) -> "AbstractMap":
        return cls(chunk)

    def __init__(self, chunk):
        self.chunk = chunk

    def load_from_saves(self, data):
        pass

    def dump_for_saves(self):
        pass

    def dump_debug_info(self, file: str):
        pass
