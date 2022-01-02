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

import mcpython.server.worldgen.map.AbstractChunkInfoMap
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class FeatureMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:feature_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.map_map: typing.Dict[typing.Tuple[str, int, int], bool] = {}

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

    def get_at_xz(self, x: int, z: int, group: str) -> bool:
        return self.map_map.setdefault((group, x, z), False)

    def set_at_xz(self, x: int, z: int, group: str):
        self.map_map[(group, x, z)] = True


if not shared.IS_TEST_ENV:
    shared.world_generation_handler.register_chunk_map(FeatureMap)
