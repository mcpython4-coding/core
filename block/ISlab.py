"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import block.Block
import event.TickHandler
import enum
import util.enums
import block.BoundingBox
from util.enums import SlabModes


BBOX_DICT = {
    SlabModes.TOP: block.BoundingBox.BoundingBox((1, 0.5, 1), (0, 0.5, 0)),
    SlabModes.BOTTOM: block.BoundingBox.BoundingBox((1, 0.5, 1)),
    SlabModes.DOUBLE: block.BoundingBox.FULL_BLOCK_BOUNDING_BOX
}


class ISlab(block.Block.Block):
    """
    base class for slabs
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.real_hit and self.real_hit[1] - self.position[1] > 0:
            self.type = SlabModes.TOP
        else:
            self.type = SlabModes.BOTTOM
        self.face_solid = {face: False for face in util.enums.EnumSide.iterate()}

    def get_model_state(self):
        return {"type": self.type.name.lower()}

    def set_model_state(self, state: dict):
        if "type" in state:
            self.type = SlabModes[state["type"].upper()]

    @staticmethod
    def get_all_model_states() -> list:
        return [{"type": x.name.upper()} for x in SlabModes]

    def on_player_interact(self, player, itemstack, button, modifiers, exact_hit) -> bool:
        # todo: add half -> double convert
        return False

    def get_view_bbox(self): return BBOX_DICT[self.type]

