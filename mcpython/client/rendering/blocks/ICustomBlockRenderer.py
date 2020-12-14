"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

from mcpython.util.annotation import onlyInClient


@onlyInClient()
class ICustomBatchBlockRenderer:
    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        raise NotImplementedError()

    def remove(self, position: typing.Tuple[int, int, int], block, data, face):
        [e.delete() for e in data]


@onlyInClient()
class ICustomDrawMethodRenderer:
    def draw(self, position: typing.Tuple[int, int, int], block):
        pass


@onlyInClient()
class ICustomBlockVertexManager:
    def handle(self, block, vertices, face, blockstate):
        pass
