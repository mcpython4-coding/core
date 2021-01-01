"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.common.block.AbstractBlock
import mcpython.common.event.TickHandler
import mcpython.util.enums
import mcpython.common.block.BoundingBox
from mcpython.util.enums import SlabModes


BBOX_DICT = {
    SlabModes.TOP: mcpython.common.block.BoundingBox.BoundingBox(
        (1, 0.5, 1), (0, 0.5, 0)
    ),
    SlabModes.BOTTOM: mcpython.common.block.BoundingBox.BoundingBox((1, 0.5, 1)),
    SlabModes.DOUBLE: mcpython.common.block.BoundingBox.FULL_BLOCK_BOUNDING_BOX,
}


class ISlab(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    base class for slabs
    """

    DEFAULT_FACE_SOLID = (
        mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )

    def __init__(self):
        super().__init__()
        self.type = SlabModes.TOP

    def on_block_added(self):
        if self.real_hit and self.real_hit[1] - self.position[1] > 0:
            self.type = SlabModes.TOP
        else:
            self.type = SlabModes.BOTTOM

    def get_model_state(self):
        return {"type": self.type.name.lower()}

    def set_model_state(self, state: dict):
        if "type" in state:
            self.type = SlabModes[state["type"].upper()]

    DEBUG_WORLD_BLOCK_STATES = [{"type": x.name.upper()} for x in SlabModes]

    def on_player_interact(
        self, player, itemstack, button, modifiers, exact_hit
    ) -> bool:
        # todo: add half -> double convert
        return False

    def get_view_bbox(self):
        return BBOX_DICT[self.type]
