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
import pyglet
from mcpython import shared
from mcpython.client.rendering.model.BoxModel import RawBoxModel


class ShulkerBoxRenderer(
    mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer
):
    """
    Class defining how a shulker box is rendered

    todo: add open / close animations
    """

    def __init__(self, texture_location: str):
        super().__init__()

        self.texture_location = texture_location
        self.texture = asyncio.get_event_loop().run_until_complete(mcpython.engine.ResourceLoader.read_pyglet_image(
            texture_location
        ))
        self.group = pyglet.graphics.TextureGroup(self.texture.get_texture())

        self.box_model = RawBoxModel(
            (0, 0, 0),
            (1, 1, 1),
            self.group,
        )

    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        return self.box_model.add_face_to_batch(batches[0], block.position, face)

    def add_multi(self, position: typing.Tuple[int, int, int], block, faces, batches):
        return self.box_model.add_faces_to_batch(batches[1], block.position, faces)

    # todo: implement these both animations
    def play_open_animation(self, block):
        pass

    def play_close_animation(self, block):
        pass
