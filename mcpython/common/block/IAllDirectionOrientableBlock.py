"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.block.AbstractBlock
import mcpython.util.enums


class IAllDirectionOrientableBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    MODEL_FACE_NAME = "facing"

    def __init__(self):
        super().__init__()
        self.face = mcpython.util.enums.EnumSide.NORTH

    def on_block_added(self):
        if self.set_to:
            sx, sy, sz = self.set_to
            px, py, pz = self.position
            dx, dy, dz = sx - px, sy - py, sz - pz
            if dx > 0:
                self.face = mcpython.util.enums.EnumSide.EAST
            elif dx < 0:
                self.face = mcpython.util.enums.EnumSide.WEST
            elif dz > 0:
                self.face = mcpython.util.enums.EnumSide.SOUTH
            elif dz < 0:
                self.face = mcpython.util.enums.EnumSide.NORTH
            elif dy > 0:
                self.face = mcpython.util.enums.EnumSide.UP
            elif dy < 0:
                self.face = mcpython.util.enums.EnumSide.DOWN

    def get_model_state(self) -> dict:
        return {self.MODEL_FACE_NAME: self.face.normal_name}

    def set_model_state(self, state: dict):
        if self.MODEL_FACE_NAME in state:
            self.face = mcpython.util.enums.EnumSide[state["facing"].upper()]

    @classmethod
    def get_all_model_states(cls) -> list:
        return [
            {cls.MODEL_FACE_NAME: face.name}
            for face in mcpython.util.enums.EnumSide.iterate()
        ]
