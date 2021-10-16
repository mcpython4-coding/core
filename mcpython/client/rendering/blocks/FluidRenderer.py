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

import mcpython.client.rendering.blocks.ICustomBlockRenderer
import mcpython.engine.ResourceLoader
import pyglet
from mcpython.client.rendering.model.BoxModel import ColoredRawBoxModel

# Used to prevent z-fighting with neighbor blocks on transparent fluids
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
        self.texture = mcpython.engine.ResourceLoader.read_pyglet_image(
            texture_location
        )
        self.texture = self.texture.get_region(
            0, 0, self.texture.width, self.texture.width
        )
        self.group = pyglet.graphics.TextureGroup(self.texture.get_texture())

        self.color = color

        self.box_model = ColoredRawBoxModel(
            (
                SOME_SMALL_VALUES / 2,
                -1 / 16 + SOME_SMALL_VALUES / 2,
                SOME_SMALL_VALUES / 2,
            ),
            (1 - SOME_SMALL_VALUES, 7 / 8 - SOME_SMALL_VALUES, 1 - SOME_SMALL_VALUES),
            self.group,
            texture_region=[(0, 0, 1, 1.0), (0, 0, 1, 1)] + [(0, 0, 1, 7 / 8)] * 6,
        )

    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        return self.box_model.add_face_to_batch(
            batches[1], block.position, face, color=self.color(block, face)
        )

    def add_multi(self, position: typing.Tuple[int, int, int], block, faces, batches):
        return self.box_model.add_face_to_batch(
            batches[1],
            block.position,
            [face.index for face in faces],
            color=self.color(block, faces[0]),
        )
