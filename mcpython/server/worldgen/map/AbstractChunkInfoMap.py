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
import io
import typing
from abc import ABC

import deprecation

from mcpython.common.world.datafixers.NetworkFixers import ChunkInfoMapFixer
from mcpython.engine.network.util import IBufferSerializeAble
from mcpython.engine.network.util import ReadBuffer
from mcpython.engine.network.util import WriteBuffer


class AbstractMap(IBufferSerializeAble, ABC):
    """
    Abstract map class holding information about a Chunk, in map-like formats
    Contains code for writing to save, by default, does nothing
    """

    NAME = None
    VERSION = 0
    DATA_FIXERS: typing.Dict[int, ChunkInfoMapFixer] = {}

    @classmethod
    def init_on(cls, chunk) -> "AbstractMap":
        return cls(chunk)

    def __init__(self, chunk):
        self.chunk = chunk

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_uint(self.VERSION)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        version = buffer.read_uint()

        if version != self.VERSION:
            while version in self.DATA_FIXERS and version != self.VERSION:
                fixer = self.DATA_FIXERS[version]

                target = WriteBuffer()

                if await fixer.apply2stream(self, buffer, target) is True:
                    buffer.stream = io.BytesIO(target.get_data())
                    break

                buffer.stream = io.BytesIO(target.get_data())

    def dump_debug_info(self, file: str):
        pass

    @deprecation.deprecated()
    def load_from_saves(self, data):
        pass
