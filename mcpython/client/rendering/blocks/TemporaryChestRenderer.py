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
from mcpython import shared


class TemporaryChestRenderer(
    mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer
):
    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        return shared.model_handler.add_raw_face_to_batch(
            block, position, {}, None, batches, face
        )
