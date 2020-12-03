"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.block.AbstractBlock
import mcpython.util.enums


class IHorizontalOrientableBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    MODEL_FACE_NAME = "facing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.face = mcpython.util.enums.EnumSide.NORTH
        if self.set_to:
            sx, sy, sz = self.set_to
            px, py, pz = self.position
            dx, dy, dz = sx - px, sy - py, sz - pz
            if dy == 0:
                if dx > 0:
                    self.face = mcpython.util.enums.EnumSide.EAST
                elif dx < 0:
                    self.face = mcpython.util.enums.EnumSide.WEST
                elif dz > 0:
                    self.face = mcpython.util.enums.EnumSide.SOUTH
                elif dz < 0:
                    self.face = mcpython.util.enums.EnumSide.NORTH

    def get_model_state(self) -> dict:
        return {self.MODEL_FACE_NAME: self.face.normal_name}

    def set_model_state(self, state: dict):
        if self.MODEL_FACE_NAME in state:
            self.face = mcpython.util.enums.EnumSide[state["facing"].upper()]

    DEBUG_WORLD_BLOCK_STATES = [{"facing": face.name} for face in mcpython.util.enums.EnumSide.iterate()[2:]]
