"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import block.Block
import globals as G
import util.enums
import block.BoundingBox


carpet_bbox = block.BoundingBox.BoundingBox((1, 1/16, 1))


def create_carpet(carpet_color: str):
    @G.registry
    class Carpet(block.Block.Block):
        @staticmethod
        def get_name() -> str: return "minecraft:{}_carpet".format(carpet_color)

        def on_block_update(self):
            x, y, z = self.position
            blockinst: block.Block.Block = G.world.get_active_dimension().get_block((x, y-1, z))
            if blockinst is None or (type(blockinst) != str and not blockinst.is_solid_side(util.enums.EnumSide.UP)):
                G.world.get_active_dimension().get_chunk_for_position((x, y, z)).remove_block(
                    (x, y, z), block_update=False)

        def is_solid_side(self, side) -> bool: return side == util.enums.EnumSide.DOWN

        def get_view_bbox(self): return carpet_bbox


for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
    create_carpet(color)
