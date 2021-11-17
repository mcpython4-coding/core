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

import mcpython.engine.event.EventHandler
from mcpython.engine.rendering.RenderingLayerManager import NORMAL_WORLD
from mcpython.util.enums import EnumSide


class ICustomBlockRenderer(ABC):
    def __init__(self):
        self.block = None

    def on_block_exposed(self, block):
        pass

    def on_block_fully_hidden(self, block):
        pass


class ICustomBatchBlockRenderer(ICustomBlockRenderer, ABC):
    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        raise NotImplementedError()

    def add_multi(self, position: typing.Tuple[int, int, int], block, faces: int, batches):
        d = []
        for face in EnumSide.iterate():
            if faces & face.bitflag:
                d.extend(self.add(position, block, face, batches))
        return d

    def remove(self, position: typing.Tuple[int, int, int], block, data, face):
        if data is not None:
            [e.delete() for e in data]

    def remove_multi(self, position: typing.Tuple[int, int, int], block, data):
        self.remove(position, block, data, None)


class ICustomDrawMethodRenderer(ICustomBlockRenderer, ABC):
    DRAW_PHASE = NORMAL_WORLD.getRenderingEvent()

    def on_block_exposed(self, block):
        def draw():
            self.draw(block.position, block)

        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            self.DRAW_PHASE, draw
        )
        block.face_info.bound_rendering_info = draw

    def on_block_fully_hidden(self, block):
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            self.DRAW_PHASE, block.face_info.bound_rendering_info
        )

    def draw(self, position: typing.Tuple[int, int, int], block):
        pass


class ICustomBlockVertexManager(ICustomBlockRenderer):
    def handle(self, block, vertices, face, blockstate):
        pass
