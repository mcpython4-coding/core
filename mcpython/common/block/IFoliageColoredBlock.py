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

import mcpython.common.block.AbstractBlock
import mcpython.util.enums
from mcpython import shared


class IFoliageColoredBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    Base class for foliage colored blocks
    """

    def get_tint_for_index(
        self, index: int
    ) -> typing.Tuple[float, float, float, float]:
        x, y, z = self.position
        biome_map = (
            shared.world.get_dimension_by_name(self.dimension)
            .get_chunk_for_position(self.position)
            .get_map("minecraft:biome_map")
        )
        return biome_map.get_biome_color_at(x, y, z) + (1,)
