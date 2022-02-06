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
from abc import ABC

import mcpython.common.block.AbstractBlock
import mcpython.engine.physics.AxisAlignedBoundingBox
import mcpython.util.enums
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack

carpet_bbox = mcpython.engine.physics.AxisAlignedBoundingBox.AxisAlignedBoundingBox(
    (1, 1 / 16, 1)
)


class AbstractCarpet(mcpython.common.block.AbstractBlock.AbstractBlock, ABC):
    """
    base class for every carpet
    """

    DEFAULT_FACE_SOLID = 0

    HARDNESS = BLAST_RESISTANCE = 0.1

    async def on_block_update(self):
        x, y, z = self.position
        dim = shared.world.get_dimension_by_name(self.dimension)
        instance: mcpython.common.block.AbstractBlock.AbstractBlock = dim.get_block(
            (x, y - 1, z)
        )

        if instance is None or (type(instance) != str and not instance.face_solid & 1):
            await dim.get_chunk_for_position((x, y, z)).remove_block(
                (x, y, z), block_update=False
            )

            shared.world.get_dimension_by_name(self.dimension).spawn_itemstack_in_world(
                ItemStack("minecraft:carpet"), self.position, pickup_delay=4
            )

    def get_view_bbox(self):
        return carpet_bbox

    @classmethod
    def modify_block_item(cls, factory):
        factory.set_fuel_level(3.35)
