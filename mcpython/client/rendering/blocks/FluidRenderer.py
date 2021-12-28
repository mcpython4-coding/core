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

import asyncio

import mcpython.client.rendering.blocks.ICustomBlockRenderer
import mcpython.engine.ResourceLoader
import mcpython.util.enums
import pyglet
from mcpython import shared
from mcpython.client.rendering.model.BoxModel import ColoredRawBoxModel

# Used to prevent z-fighting with neighbor blocks on transparent fluids
from mcpython.engine import logger

SOME_SMALL_VALUES = 1 / 1000


class FluidRenderer(
    mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer
):
    """
    Class defining how a fluid block is rendered
    """

    def __init__(self, texture_location: str, color=lambda *_: (1, 1, 1, 1)):
        super().__init__()

        self.texture_location = texture_location

        self.texture = None
        self.group = None
        shared.tick_handler.schedule_once(self.reload())

        self.color = color

        self.layered_models = [
            ColoredRawBoxModel(
                (
                    SOME_SMALL_VALUES / 2,
                    -(0.5 - i / 16) + SOME_SMALL_VALUES / 2,
                    SOME_SMALL_VALUES / 2,
                ),
                (
                    1 - SOME_SMALL_VALUES,
                    i / 8 - SOME_SMALL_VALUES,
                    1 - SOME_SMALL_VALUES,
                ),
                self.group,
                texture_region=[(0, 0, 1, 1.0), (0, 0, 1, 1)] + [(0, 0, 1, i / 8)] * 6,
            )
            for i in range(1, 8)
        ]

    async def reload(self):
        try:
            self.texture = await mcpython.engine.ResourceLoader.read_pyglet_image(
                self.texture_location
            )
        except (ValueError, FileNotFoundError):
            self.texture = await mcpython.engine.ResourceLoader.read_pyglet_image(
                "assets/missing_texture.png"
            )
            self.texture_location = "assets/missing_texture.png"

            if shared.IS_CLIENT:
                logger.println(
                    f"[FLUID][WARN] could not look up fluid texture {self.texture_location}!"
                )

        self.texture = self.texture.get_region(
            0, 0, self.texture.width, self.texture.width
        )
        self.group = pyglet.graphics.TextureGroup(self.texture.get_texture())

        for layer in self.layered_models:
            layer.texture = self.group

    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        return self.layered_models[block.height - 1].add_face_to_batch(
            batches[1], block.position, face, color=self.color(block, face)
        )

    def add_multi(
        self, position: typing.Tuple[int, int, int], block, faces: int, batches
    ):
        return self.layered_models[block.height - 1].add_faces_to_batch(
            batches[1],
            block.position,
            faces,
            color=self.color(block, faces),
        )
