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
import math
import time
from abc import ABC

from mcpython.common.block.AbstractBlock import AbstractBlock
from mcpython import shared
from mcpython.engine import logger
from mcpython.util.enums import EnumSide
import mcpython.common.block.PossibleBlockStateBuilder


SHAPES = [
    "north_south",
    "east_west",
    "ascending_north",
    "ascending_east",
    "ascending_south",
    "ascending_west",
]


class IRail(AbstractBlock, ABC):
    HARDNESS = .5
    BLAST_RESISTANCE = .5

    IS_SOLID = False
    DEFAULT_FACE_SOLID = AbstractBlock.UNSOLID_FACE_SOLID

    def is_currently_orientated_for_side(self, side: EnumSide) -> bool:
        return False


class ActivatorRail(IRail):
    NAME = "minecraft:activator_rail"

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .combinations()
        .add_comby_bool("powered")
        .add_comby("shape", SHAPES)
        .build()
    )

    def __init__(self):
        super().__init__()

        self.shape = "north_south"
        self.force_active = False

    def get_model_state(self) -> dict:
        return {"shape": self.shape, "powered": str(any(self.injected_redstone_power) or self.force_active).lower()}

    def set_model_state(self, state: dict):
        if "shape" in state:
            self.shape = state["shape"]

        if "powered" in state:
            self.force_active = state["powered"] == "true"

    def on_block_update(self):
        x, y, z = self.position
        dimension = shared.world.get_dimension_by_name(self.dimension)

        connecting_faces = set()
        for face in EnumSide.iterate()[2:]:
            block = dimension.get_block((x+face.dx, y, z+face.dz))
            if isinstance(block, IRail) and block.is_currently_orientated_for_side(face.invert()):
                connecting_faces.add(face)

        if self.shape in ("north_south", "ascending_south", "ascending_south"):
            if not (EnumSide.EAST in connecting_faces or EnumSide.WEST in connecting_faces):
                self.shape = "east_west"

        elif self.shape in ("east_west", "ascending_east", "ascending_west"):
            if not (EnumSide.NORTH in connecting_faces or EnumSide.SOUTH in connecting_faces):
                self.shape = "north_south"


