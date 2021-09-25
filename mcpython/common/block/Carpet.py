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
import mcpython.common.block.BoundingBox
import mcpython.common.container.ResourceStack
import mcpython.util.enums
from mcpython import shared

carpet_bbox = mcpython.common.block.BoundingBox.BoundingBox((1, 1 / 16, 1))


class AbstractCarpet(mcpython.common.block.AbstractBlock.AbstractBlock, ABC):
    """
    base class for every carpet
    """

    DEFAULT_FACE_SOLID = (
        mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )

    def on_block_update(self):
        x, y, z = self.position
        dim = shared.world.get_dimension_by_name(self.dimension)
        instance: mcpython.common.block.AbstractBlock.AbstractBlock = dim.get_block(
            (x, y - 1, z)
        )
        if instance is None or (
            type(instance) != str
            and not instance.face_solid[0]
        ):
            dim.get_chunk_for_position((x, y, z)).remove_block(
                (x, y, z), block_update=False
            )
            shared.world.get_active_player().pick_up_item(
                mcpython.common.container.ResourceStack.ItemStack("minecraft:carpet")
            )  # todo: drop in world

    def get_view_bbox(self):
        return carpet_bbox

    @classmethod
    def modify_block_item(cls, factory):
        factory.set_fuel_level(3.35)


def create_carpet_block(carpet_color: str):
    """
    generator function for carpets. Will create an new class for an carpet
    :param carpet_color: the color name of the carpet
    :return: the generated class
    """

    @shared.registry
    class Carpet(AbstractCarpet):
        NAME: str = "{}_carpet".format(carpet_color)  # the name of the block

    return Carpet


def load():
    for color in mcpython.util.enums.COLORS:
        create_carpet_block("minecraft:" + color)
