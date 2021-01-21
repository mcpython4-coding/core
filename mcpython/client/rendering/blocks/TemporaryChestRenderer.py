"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.client.rendering.blocks.ICustomBlockRenderer
from mcpython import shared


class TemporaryChestRenderer(
    mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer
):
    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        return shared.model_handler.add_raw_face_to_batch(
            position, {}, None, batches, face
        )
