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

from mcpython.common.world.datafixers.NetworkFixers import ChunkInfoMapFixer
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer


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
            logger.println(
                f"Applying data fixer from version {version} to version {self.VERSION} onto data map {self.NAME} at chunk {self.chunk}"
            )

            while version in self.DATA_FIXERS and version != self.VERSION:
                fixer = self.DATA_FIXERS[version]

                logger.println(
                    f"[INTERNAL] Applying data transformer from {version} to {fixer.AFTER_VERSION}: {fixer}"
                )

                target = WriteBuffer()

                if await fixer.apply2stream(self, buffer, target) is True:
                    buffer.stream = io.BytesIO(target.get_data())
                    break

                buffer.stream = io.BytesIO(target.get_data())
                version = fixer.AFTER_VERSION

        if version != self.VERSION:
            logger.println(
                "[FATAL] failed to data fix the full data structure; no full migration path found!"
            )

    def dump_debug_info(self, file: str):
        pass
