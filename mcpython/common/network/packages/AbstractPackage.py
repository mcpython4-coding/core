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


class AbstractPackage(ABC):
    PACKAGE_ID = -1  # set only to an positive value if you know what you are doing!
    ASSIGNED_CHANNEL: str = None  # the channel instance name to send over

    @classmethod
    def decode_package(cls, stream) -> "AbstractPackage":
        raise NotImplementedError()

    def __init__(self):
        self.package_number = -1
        self.response_stack = tuple()

    def respond(self, package: "AbstractPackage"):
        pass  # todo: implement

    def serialize(self) -> bytes:
        raise NotImplementedError()
