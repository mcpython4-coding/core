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
from mcpython.client.rendering.model.BoxModel import MutableRawBoxModel, RawBoxModel
from mcpython.client.rendering.model.util import calculate_default_layout_uvs
from mcpython.util.enums import EnumSide


class IChestRendererSupport:
    def __init__(self):
        self.position = None
        self.face_info = None

    DEFAULT_DISPLAY_NAME = "Chest"


TEXTURE_COORDS_TOP = calculate_default_layout_uvs((64, 64), (15, 5, 15), (0, 64 - 18))
TEXTURE_COORDS_BOTTOM = calculate_default_layout_uvs(
    (64, 64), (15, 10, 15), (0, 64 - 42)
)

TEXTURE_COORDS_LOCK = calculate_default_layout_uvs((64, 64), (1, 2, 2), (0, 64 - 4))


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
        self.texture = None
        self.group = None

        self.box_model_top = None
        self.box_model_bottom = None
        self.lock_model = None

        shared.tick_handler.schedule_once(self.reload())

    async def reload(self):
        self.texture = await mcpython.engine.ResourceLoader.read_pyglet_image(
            self.texture_location
        )
        self.group = pyglet.graphics.TextureGroup(self.texture.get_texture())

        self.box_model_top = MutableRawBoxModel(
            (0, -0.5 + 14 / 24 + 7 / 48 + 1 / 16, 0),
            (7 / 8, 7 / 24, 7 / 8),
            self.group,
            TEXTURE_COORDS_TOP,
        )
        self.box_model_bottom = RawBoxModel(
            (0, -0.5 + 14 / 48 + 1 / 16, 0),
            (7 / 8, 14 / 24, 7 / 8),
            self.group,
            TEXTURE_COORDS_BOTTOM,
        )
        self.lock_model = RawBoxModel(
            (0.4 + 1 / 16, 1 / 8, 0),
            (1 / 16, 1 / 8, 1 / 8),
            self.group,
            TEXTURE_COORDS_LOCK,
        )

    def add(
        self,
        position: typing.Tuple[int, int, int],
        block: IChestRendererSupport,
        face,
        batches,
    ):
        return (
            self.box_model_top.add_face_to_batch(batches[0], block.position, face)
            + self.box_model_bottom.add_face_to_batch(batches[0], block.position, face)
            + self.lock_model.add_face_to_batch(batches[0], block.position, face)
        )

    def add_multi(
        self,
        position: typing.Tuple[int, int, int],
        block: IChestRendererSupport,
        faces: int,
        batches,
    ):
        faces = [face.index for face in EnumSide.iterate() if faces & face.bitflag]
        return (
            self.box_model_top.add_face_to_batch(batches[0], block.position, faces)
            + self.box_model_bottom.add_face_to_batch(batches[0], block.position, faces)
            + self.lock_model.add_face_to_batch(batches[0], block.position, faces)
        )

    # todo: implement these both animations
    def play_open_animation(self, block: IChestRendererSupport):
        # self.box_model_top.mutate_add_face_to_batch(
        #     block.face_info.multi_data,
        #     block.position,
        #     None,
        #     rotation=(90, 0, 0),
        # )
        pass

    def play_close_animation(self, block: IChestRendererSupport):
        # self.box_model_top.mutate_add_face_to_batch(
        #     block.face_info.multi_data,
        #     block.position,
        #     None,
        #     rotation=(0, 0, 0),
        # )
        pass
