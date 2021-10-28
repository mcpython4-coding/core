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
import mcpython.common.block.AbstractBlock
import mcpython.common.event.TickHandler
from mcpython import shared


class FlowerLikeBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    Base class for flower-like blocks
    """

    SUPPORT_BLOCK_TAG = "#minecraft:plant_support"

    HARDNESS = BLAST_RESISTANCE = 0

    def on_block_update(self):
        x, y, z = self.position
        dimension = shared.world.get_dimension_by_name(self.dimension)
        block_under = dimension.get_block((x, y - 1, z), none_if_str=True)

        if block_under is None or self.SUPPORT_BLOCK_TAG not in block_under.TAGS:
            dimension.remove_block(self, block_update_self=False)
