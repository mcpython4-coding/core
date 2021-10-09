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

import mcpython.util.enums
from mcpython import shared

from . import AbstractBlock


class GrassBlock(AbstractBlock.AbstractBlock):
    """
    Class for the grass block
    """

    NAME = "minecraft:grass_block"

    HARDNESS = 0.5
    BLAST_RESISTANCE = 0.5
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.SHOVEL]

    ENABLE_RANDOM_TICKS = True

    def get_model_state(self) -> dict:
        return {"snowy": "false"}

    def on_random_update(self):
        x, y, z = self.position
        dim = shared.world.get_dimension_by_name(self.dimension)

        for dy in range(y + 1, dim.get_world_height_range()[1] + 1):
            instance = dim.get_block((x, dy, z))
            if instance is not None:
                break

        else:
            instance = dim.get_block((x, y + 1, z), none_if_str=True)
            if instance is not None and (
                instance.face_solid[0] or instance.face_solid[1]
            ):
                dim.get_chunk_for_position(self.position).add_block(
                    self.position, "minecraft:dirt"
                )

    @staticmethod
    def get_tint_for_index(index: int) -> typing.Tuple[float, float, float, float]:
        # todo: make biome-based
        return 91/255, 201/255, 59/255, 1
