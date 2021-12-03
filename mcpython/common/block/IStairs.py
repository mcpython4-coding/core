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
import enum

import mcpython.common.block.AbstractBlock
import mcpython.common.block.PossibleBlockStateBuilder
import mcpython.engine.physics.AxisAlignedBoundingBox
import mcpython.util.enums
from mcpython.common.block.IHorizontalOrientableBlock import IHorizontalOrientableBlock
from mcpython.util.enums import EnumSide


class StairShape(enum.Enum):
    STRAIGHT = 0
    INNER_LEFT = 1
    INNER_RIGHT = 2
    OUTER_LEFT = 3
    OUTER_RIGHT = 4


class IStairs(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    Base class for stairs

    todo: implement bounding box
    """

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .combinations()
        .add_comby_side_horizontal("facing")
        .add_comby("half", "top", "bottom")
        .add_comby(
            "shape",
            "straight",
            "inner_left",
            "inner_right",
            "outer_left",
            "outer_right",
        )
        .build()
    )

    def __init__(self):
        super().__init__()
        self.face = EnumSide.NORTH
        self.is_top = False
        self.shape = StairShape.STRAIGHT

    def on_block_added(self):
        IHorizontalOrientableBlock.on_block_added(self)

        if self.real_hit and self.real_hit[1] > self.position[1]:
            self.is_top = True
            self.schedule_network_update()

    def on_block_update(self):
        pass  # todo: calculate shape!

    def get_model_state(self):
        return {
            "facing": self.face.normal_name,
            "half": "top" if self.is_top else "bottom",
            "shape": self.shape.name.lower(),
        }

    def set_model_state(self, state: dict):
        if "facing" in state:
            self.face = EnumSide[state["facing"].upper()]

        if "half" in state:
            self.is_top = state["half"] == "top"

        if "shape" in state:
            self.shape = StairShape[state["shape"].upper()]

    def get_view_bbox(self):
        return mcpython.engine.physics.AxisAlignedBoundingBox.FULL_BLOCK_BOUNDING_BOX
