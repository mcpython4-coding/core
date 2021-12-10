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

from mcpython.engine.network.util import IBufferSerializeAble


class ISerializeAble(IBufferSerializeAble, ABC):
    SERIALIZER: typing.Optional[typing.Type["ISerializer"]] = None

    @classmethod
    async def deserialize(cls, data: bytes) -> "ISerializeAble":
        return await cls.SERIALIZER.deserialize(data)

    async def serialize(self) -> bytes:
        return await self.SERIALIZER.serialize(self)


class ISerializer:
    @classmethod
    async def check(cls, data: bytes) -> bool:
        return True

    @classmethod
    async def deserialize(cls, data: bytes) -> ISerializeAble:
        raise NotImplementedError()

    @classmethod
    async def serialize(cls, obj: ISerializeAble) -> bytes:
        raise NotImplementedError()
