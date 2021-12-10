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

import mcpython.common.block.PossibleBlockStateBuilder
from mcpython import shared
from mcpython.common.block.AbstractBlock import AbstractBlock
from mcpython.engine import logger
from mcpython.util.enums import EnumSide

SHAPES = [
    "north_south",
    "east_west",
    "ascending_north",
    "ascending_east",
    "ascending_south",
    "ascending_west",
]


class IRail(AbstractBlock, ABC):
    HARDNESS = 0.5
    BLAST_RESISTANCE = 0.5

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0
    NO_ENTITY_COLLISION = True

    def is_currently_orientated_for_side(self, side: EnumSide, up: bool) -> bool:
        return False


class IStraightRail(IRail, ABC):
    def __init__(self):
        super().__init__()

        self.shape = "north_south"

    def get_model_state(self) -> dict:
        return {"shape": self.shape}

    def set_model_state(self, state: dict):
        if "shape" in state:
            self.shape = state["shape"]

    async def on_block_update(self):
        x, y, z = self.position
        dimension = shared.world.get_dimension_by_name(self.dimension)

        connecting_faces = set()
        for face in EnumSide.iterate()[2:]:
            block = dimension.get_block((x + face.dx, y, z + face.dz))
            if isinstance(block, IRail) and block.is_currently_orientated_for_side(
                face.invert(), False
            ):
                connecting_faces.add(face)

        if self.shape in ("north_south", "ascending_south", "ascending_south"):
            if not (
                EnumSide.EAST in connecting_faces or EnumSide.WEST in connecting_faces
            ):
                self.shape = "east_west"

        elif self.shape in ("east_west", "ascending_east", "ascending_west"):
            if not (
                EnumSide.NORTH in connecting_faces or EnumSide.SOUTH in connecting_faces
            ):
                self.shape = "north_south"

        self.face_info.update(True)
        await self.schedule_network_update()

    def is_currently_orientated_for_side(self, side: EnumSide, up: bool) -> bool:
        if "ascending" in self.shape:
            if self.shape == "ascending_" + side.normal_name and up:
                return True
            elif self.shape == "ascending_" + side.invert().normal_name and not up:
                return True
            return False
        return side.normal_name in self.shape


class ActivatorRail(IStraightRail):
    NAME = "minecraft:activator_rail"

    BLAST_RESISTANCE = HARDNESS = 0.7
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.PICKAXE}

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .combinations()
        .add_comby_bool("powered")
        .add_comby("shape", SHAPES)
        .build()
    )

    def __init__(self):
        super().__init__()
        self.force_active = False

    def get_model_state(self) -> dict:
        return super().get_model_state() | {
            "powered": str(
                any(self.injected_redstone_power) or self.force_active
            ).lower(),
        }

    def set_model_state(self, state: dict):
        super().set_model_state(state)

        if "powered" in state:
            self.force_active = state["powered"] == "true"


class PoweredRail(ActivatorRail):
    NAME = "minecraft:powered_rail"

    BLAST_RESISTANCE = HARDNESS = 0.7
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.PICKAXE}


class DetectorRail(ActivatorRail):
    NAME = "minecraft:detector_rail"

    BLAST_RESISTANCE = HARDNESS = 0.7
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.PICKAXE}
