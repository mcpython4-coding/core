import block.Block
import util.enums


class IHorizontalOrientableBlock(block.Block.Block):
    MODEL_FACE_NAME = "facing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.face = util.enums.EnumSide.NORTH
        if self.set_to:
            sx, sy, sz = self.set_to
            px, py, pz = self.position
            dx, dy, dz = sx - px, sy - py, sz - pz
            if dy == 0:
                if dx > 0:
                    self.face = util.enums.EnumSide.NORTH
                elif dx < 0:
                    self.face = util.enums.EnumSide.SOUTH
                elif dz > 0:
                    self.face = util.enums.EnumSide.EAST
                elif dz < 0:
                    self.face = util.enums.EnumSide.WEST

    def get_model_state(self) -> dict:
        return {self.MODEL_FACE_NAME: self.face.normal_name}

    def set_model_state(self, state: dict):
        if self.MODEL_FACE_NAME in state:
            self.face = util.enums.EnumSide[state["facing"].upper()]

    @classmethod
    def get_all_model_states(cls) -> list:
        return [{cls.MODEL_FACE_NAME: face.name} for face in util.enums.EnumSide.iterate()[2:]]

