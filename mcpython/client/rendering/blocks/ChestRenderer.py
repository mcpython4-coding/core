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
from mcpython import shared
from mcpython.client.rendering.model.BoxModel import RawBoxModel, MutableRawBoxModel
from mcpython.client.rendering.model.util import calculate_default_layout_uvs


class IChestRendererSupport:
    DEFAULT_DISPLAY_NAME = "Chest"


TEXTURE_COORDS_TOP = calculate_default_layout_uvs((64, 64), (15, 5, 15), (0, 64 - 18))
TEXTURE_COORDS_BOTTOM = calculate_default_layout_uvs(
    (64, 64), (15, 10, 15), (0, 64 - 42)
)


class ChestRenderer(
    mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer
):
    """
    Class defining how a chest is rendered

    todo: add open / close animations
    """

    def __init__(self, texture_location: str):
        super().__init__()

        self.texture_location = texture_location
        self.texture = mcpython.engine.ResourceLoader.read_pyglet_image(
            texture_location
        )
        self.group = pyglet.graphics.TextureGroup(self.texture.get_texture())

        self.box_model_top = MutableRawBoxModel(
            (0, 0.5 - 7 / 48, 0), (7 / 8, 7 / 24, 7 / 8), self.group, TEXTURE_COORDS_TOP
        )
        self.box_model_bottom = RawBoxModel(
            (0, -(0.5 - 14 / 48), 0),
            (7 / 8, 14 / 24, 7 / 8),
            self.group,
            TEXTURE_COORDS_BOTTOM,
        )

    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        self.box_model_top.add_face_to_batch(batches[0], block.position, face)
        self.box_model_bottom.add_face_to_batch(batches[0], block.position, face)

    # todo: implement these both animations
    def play_open_animation(self, block: IChestRendererSupport):
        pass

    def play_close_animation(self, block: IChestRendererSupport):
        pass