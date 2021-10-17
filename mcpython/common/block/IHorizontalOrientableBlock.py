"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.block.AbstractBlock
import mcpython.util.enums


class IHorizontalOrientableBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    MODEL_FACE_NAME = "facing"

    def __init__(self):
        super().__init__()
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

                self.schedule_network_update()

    def get_model_state(self) -> dict:
        return {self.MODEL_FACE_NAME: self.face.normal_name}

    def set_model_state(self, state: dict):
        if self.MODEL_FACE_NAME in state:
            self.face = mcpython.util.enums.EnumSide[
                state[self.MODEL_FACE_NAME].upper()
            ]

    DEBUG_WORLD_BLOCK_STATES = []

    def __init_subclass__(cls, **kwargs):
        cls.DEBUG_WORLD_BLOCK_STATES = [
            {cls.MODEL_FACE_NAME: face.name}
            for face in mcpython.util.enums.EnumSide.iterate()[2:]
        ]
