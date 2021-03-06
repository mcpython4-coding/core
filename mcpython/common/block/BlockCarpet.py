"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.block.AbstractBlock
import mcpython.common.block.BoundingBox
from mcpython import shared
import mcpython.common.container.ItemStack
import mcpython.util.enums

carpet_bbox = mcpython.common.block.BoundingBox.BoundingBox((1, 1 / 16, 1))


class ICarpet(mcpython.common.block.AbstractBlock.AbstractBlock):
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
            and not instance.face_solid[mcpython.util.enums.EnumSide.UP]
        ):
            dim.get_chunk_for_position((x, y, z)).remove_block(
                (x, y, z), block_update=False
            )
            shared.world.get_active_player().pick_up_item(
                mcpython.common.container.ItemStack.ItemStack("minecraft:carpet")
            )  # todo: drop in world

    def get_view_bbox(self):
        return carpet_bbox

    @classmethod
    def modify_block_item(cls, factory):
        factory.set_fuel_level(3.35)


def create_carpet(carpet_color: str):
    """
    generator function for carpets. Will create an new class for an carpet
    :param carpet_color: the color name of the carpet
    :return: the generated class
    """

    @shared.registry
    class Carpet(ICarpet):
        NAME: str = "{}_carpet".format(carpet_color)  # the name of the block

    return Carpet


@shared.mod_loader("minecraft", "stage:block:load")
def load():
    for color in mcpython.util.enums.COLORS:
        create_carpet("minecraft:" + color)
