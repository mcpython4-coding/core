"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import block.Block
import block.BoundingBox
import globals as G
import gui.ItemStack
import util.enums

carpet_bbox = block.BoundingBox.BoundingBox((1, 1 / 16, 1))


class ICarpet(block.Block.Block):
    """
    base class for every carpet
    """

    def __init__(self, *args, **kwargs):
        """
        creates an new carpet class
        """
        super().__init__(*args, **kwargs)
        self.face_solid = {face: face == util.enums.EnumSide.DOWN for face in util.enums.EnumSide.iterate()}

    def on_block_update(self):
        x, y, z = self.position
        blockinst: block.Block.Block = G.world.get_active_dimension().get_block((x, y - 1, z))
        if blockinst is None or (type(blockinst) != str and not blockinst.face_solid[util.enums.EnumSide.UP]):
            G.world.get_active_dimension().get_chunk_for_position((x, y, z)).remove_block(
                (x, y, z), block_update=False)
            G.world.get_active_player().pick_up(gui.ItemStack.ItemStack("minecraft:carpet"))

    def get_view_bbox(self): return carpet_bbox

    @classmethod
    def modify_block_item(cls, itemfactory):
        itemfactory.setFuelLevel(3.35)


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


for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
    create_carpet("minecraft:" + color)
