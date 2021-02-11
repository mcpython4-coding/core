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
import mcpython.server.worldgen.map.AbstractChunkInfoMap
import typing
from mcpython import shared


@shared.world_generation_handler
class FeatureMap(mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap):
    NAME = "minecraft:feature_map"

    def __init__(self, chunk):
        super().__init__(chunk)
        self.temperature_map: typing.Dict[typing.Tuple[int, int, int], float] = {}

    def load_from_saves(self, data):
        pass

    def dump_for_saves(self):
        pass

    def get_at_xz(self, x: int, z: int, group: str) -> str:
        pass

    def set_at_xz(self, x: int, z: int, biome: str, group: str):
        pass
