"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.block.AbstractBlock
import mcpython.common.block.BoundingBox
from mcpython import shared as G
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
        dim = G.world.get_dimension_by_name(self.dimension)
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
            G.world.get_active_player().pick_up(
                mcpython.common.container.ItemStack.ItemStack("minecraft:carpet")
            )  # todo: drop in world

    def get_view_bbox(self):
        return carpet_bbox

    @classmethod
    def modify_block_item(cls, factory):
        factory.setFuelLevel(3.35)


def create_carpet(carpet_color: str):
    """
    generator function for carpets. Will create an new class for an carpet
    :param carpet_color: the color name of the carpet
    :return: the generated class
    """

    @G.registry
    class Carpet(ICarpet):
        NAME: str = "{}_carpet".format(carpet_color)  # the name of the block

    return Carpet


@G.mod_loader("minecraft", "stage:block:load")
def load():
    for color in mcpython.util.enums.COLORS:
        create_carpet("minecraft:" + color)
