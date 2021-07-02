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


class ISerializeAble(ABC):
    SERIALIZER: typing.Optional[typing.Type["ISerializer"]] = None

    @classmethod
    def deserialize(cls, data: bytes) -> "ISerializeAble":
        return cls.SERIALIZER.deserialize(data)

    def serialize(self) -> bytes:
        return self.SERIALIZER.serialize(self)


class ISerializer:
    @classmethod
    def check(cls, data: bytes) -> bool:
        return True

    @classmethod
    def deserialize(cls, data: bytes) -> ISerializeAble:
        raise NotImplementedError()

    @classmethod
    def serialize(cls, obj: ISerializeAble) -> bytes:
        raise NotImplementedError()
