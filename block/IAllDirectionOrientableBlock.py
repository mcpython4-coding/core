"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import block.Block
import util.enums


class IAllDirectionOrientableBlock(block.Block.Block):
    MODEL_FACE_NAME = "facing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.face = util.enums.EnumSide.NORTH
        if self.set_to:
            sx, sy, sz = self.set_to
            px, py, pz = self.position
            dx, dy, dz = sx - px, sy - py, sz - pz
            if dx > 0:
                self.face = util.enums.EnumSide.NORTH
            elif dx < 0:
                self.face = util.enums.EnumSide.SOUTH
            elif dz > 0:
                self.face = util.enums.EnumSide.EAST
            elif dz < 0:
                self.face = util.enums.EnumSide.WEST
            elif dy > 0:
                self.face = util.enums.EnumSide.UP
            elif dy < 0:
                self.face = util.enums.EnumSide.DOWN

    def get_model_state(self) -> dict:
        return {self.MODEL_FACE_NAME: self.face.normal_name}

    def set_model_state(self, state: dict):
        if self.MODEL_FACE_NAME in state:
            self.face = util.enums.EnumSide[state["facing"].upper()]

    @classmethod
    def get_all_model_states(cls) -> list:
        return [{cls.MODEL_FACE_NAME: face.name} for face in util.enums.EnumSide.iterate()]

