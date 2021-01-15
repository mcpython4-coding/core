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
import typing
import socket
import enum


class SideType(enum.Enum):
    CLIENT = 0
    SERVER = 1


class AbstractNetworkConnection(ABC):
    def __init__(self, side: SideType):
        self.side = side

    def send_data(self, data: bytes):
        raise NotImplementedError()

    def has_data(self) -> bool:
        raise NotImplementedError()

    def receive_package(self) -> typing.Iterator[bytes]:
        raise NotImplementedError()


class SocketNetworkConnection(AbstractNetworkConnection):
    pass


class ClientInnerServerConnection(AbstractNetworkConnection):
    pass
