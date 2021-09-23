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

from mcpython.engine.rendering.RenderingLayerManager import NORMAL_WORLD
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class ICustomBatchBlockRenderer:
    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        raise NotImplementedError()

    def remove(self, position: typing.Tuple[int, int, int], block, data, face):
        [e.delete() for e in data]


@onlyInClient()
class ICustomDrawMethodRenderer:
    DRAW_PHASE = NORMAL_WORLD.getRenderingEvent()

    def draw(self, position: typing.Tuple[int, int, int], block):
        pass


@onlyInClient()
class ICustomBlockVertexManager:
    def handle(self, block, vertices, face, blockstate):
        pass
