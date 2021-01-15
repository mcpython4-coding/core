"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

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
