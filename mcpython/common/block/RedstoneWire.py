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
import typing

import mcpython.engine.physics.AxisAlignedBoundingBox
from mcpython import shared
from mcpython.util.enums import EnumSide

from . import AbstractBlock
from .PossibleBlockStateBuilder import PossibleBlockStateBuilder

states = "none", "up", "side"


redstone_wire_bbox = (
    mcpython.engine.physics.AxisAlignedBoundingBox.AxisAlignedBoundingBox(
        (1, 1 / 16, 1)
    )
)


class RedstoneWire(AbstractBlock.AbstractBlock):
    NAME: str = "minecraft:redstone_wire"

    HARDNESS = BLAST_RESISTANCE = 0

    DEBUG_WORLD_BLOCK_STATES = (
        PossibleBlockStateBuilder()
        .add_comby("north", *states)
        .add_comby("east", *states)
        .add_comby("south", *states)
        .add_comby("west", *states)
        .build()
    )

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0
    NO_ENTITY_COLLISION = True

    def __init__(self):
        super().__init__()
        self.state = {
            EnumSide.N: "none",
            EnumSide.E: "none",
            EnumSide.S: "none",
            EnumSide.W: "none",
        }
        self.level = 0

    def get_model_state(self) -> dict:
        return {key.normal_name: state for key, state in self.state.items()}

    def set_model_state(self, state: dict):
        self.state.update({EnumSide[e.upper()]: v for e, v in state.items()})

    def on_block_update(self):
        self.update_visual()
        self.send_level_update()

        x, y, z = self.position
        dimension = shared.world.get_dimension_by_name(self.dimension)
        block = dimension.get_block((x, y - 1, z), none_if_str=True)
        if block is None or not block.face_solid & 1:
            dimension.remove_block(self.position)
            return

        elif block.IS_SOLID:
            block.inject_redstone_power(EnumSide.UP, self.level)

        self.schedule_network_update()

    def send_level_update(self):
        level = max(self.injected_redstone_power)
        if level != self.level:
            self.level = level
            shared.world.get_dimension_by_name(self.dimension).on_block_updated(
                self.position, include_itself=False
            )

    def update_visual(self):
        x, y, z = self.position

        dimension = shared.world.get_dimension_by_name(self.dimension)

        block = dimension.get_block((x, y + 1, z), none_if_str=True)
        non_solid_above = block is None or not block.face_solid & 2

        for face in EnumSide.iterate()[2:]:
            block = dimension.get_block((x + face.dx, y, z + face.dz), none_if_str=True)

            if isinstance(block, AbstractBlock.AbstractBlock):
                if block.is_connecting_to_redstone(face.invert()):
                    self.state[face] = "side"

                elif not block.face_solid & 2:
                    block2 = dimension.get_block(
                        (x + face.dx, y - 1, z + face.dz), none_if_str=True
                    )

                    if isinstance(block2, RedstoneWire):
                        self.state[face] = "side"
                    else:
                        block.inject_redstone_power(face.invert(), 0)
                        continue
                else:
                    block.inject_redstone_power(face.invert(), 0)
                    continue

                block.inject_redstone_power(face.invert(), self.level)

        if non_solid_above:
            for face in EnumSide.iterate()[2:]:
                block = dimension.get_block(
                    (x + face.dx, y + 1, z + face.dz), none_if_str=True
                )
                if isinstance(block, RedstoneWire):
                    self.state[face] = "up"

        self.face_info.update(True)

    def get_redstone_source_power(self, side: EnumSide) -> int:
        return self.level if side != EnumSide.UP else 0

    def is_connecting_to_redstone(self, side: EnumSide) -> bool:
        return side != EnumSide.UP

    def get_tint_for_index(
        self, index: int
    ) -> typing.Tuple[float, float, float, float]:
        f = (self.level + 1) / 16
        return f, 0, 0, 1

    def get_view_bbox(self):
        return redstone_wire_bbox
