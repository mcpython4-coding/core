"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing
import enum

import mcpython.client.rendering.blocks.ICustomBlockRenderer
import mcpython.ResourceLoader
import mcpython.client.rendering.BoxModel


class ChestTypes(enum.Enum):
    SINGLE = 0
    LEFT = 1
    RIGHT = 2


class IChestRenderAble:
    def get_type(self) -> ChestTypes:
        return ChestTypes.SINGLE


class ChestRenderer(
    mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer
):
    """
    Block Renderer for any chest-like texture, single or double
    """

    def __init__(
        self, single_texture: str, left_double: str = None, right_double: str = None
    ):
        self.single_box_top = mcpython.client.rendering.BoxModel.BaseBoxModel(
            (1 / 16, 10 / 16, 1 / 16), (14 / 16, 5 / 16, 14 / 16), single_texture,
        ).auto_value_region((0, 0), (14 / 64, 5 / 64, 14 / 64))
        self.single_box_bottom = mcpython.client.rendering.BoxModel.BaseBoxModel(
            (1 / 16, 1 / 16, 1 / 16), (14 / 16, 10 / 16, 14 / 16), single_texture,
        ).auto_value_region((0, 19/64), (14 / 64, 10 / 64, 14 / 64))

    def add(self, position: typing.Tuple[int, int, int], block: IChestRenderAble, face, batches):
        print(block.get_type())
        if block.get_type() == ChestTypes.SINGLE:
            return self.single_box_bottom.add_face_to_batch(batches[0], block.position, face.as_bit()) + \
                self.single_box_top.add_face_to_batch(batches[0], block.position, face.as_bit())
        return []
