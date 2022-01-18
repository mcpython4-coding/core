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
from .IHorizontalOrientableBlock import IHorizontalOrientableBlock
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

    async def set_model_state(self, state: dict):
        self.state.update({EnumSide[e.upper()]: v for e, v in state.items()})

    async def on_block_update(self):
        self.update_visual()
        await self.send_level_update()

        x, y, z = self.position
        dimension = shared.world.get_dimension_by_name(self.dimension)
        block = dimension.get_block((x, y - 1, z), none_if_str=True)
        if block is None or not block.face_solid & EnumSide.UP.bitflag:
            await dimension.remove_block(self.position)
            return

        elif block.IS_SOLID:
            block.inject_redstone_power(EnumSide.UP, self.level)
            await block.on_redstone_update()

        await self.schedule_network_update()

    async def send_level_update(self):
        dimension = shared.world.get_dimension_by_name(self.dimension)

        level = 0
        for face in EnumSide.iterate():
            pos = face.relative_offset(self.position)
            block = dimension.get_block(pos, none_if_str=True)

            if block is not None:
                level = max(level, block.get_redstone_output(face.invert()))

        if level != self.level:
            self.level = level

            await shared.world.get_dimension_by_name(self.dimension).get_chunk_for_position(self.position).on_block_updated(
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
        return side != EnumSide.UP and side != EnumSide.DOWN

    def get_tint_for_index(
        self, index: int
    ) -> typing.Tuple[float, float, float, float]:
        f = (self.level + 1) / 16
        return f, 0, 0, 1

    def get_view_bbox(self):
        return redstone_wire_bbox


class RedstoneBlock(AbstractBlock.AbstractBlock):
    NAME = "minecraft:redstone_block"

    def get_redstone_output(self, side: mcpython.util.enums.EnumSide) -> int:
        return 15

    def get_redstone_source_power(self, side: mcpython.util.enums.EnumSide) -> int:
        return 15

    def is_connecting_to_redstone(self, side: mcpython.util.enums.EnumSide) -> bool:
        return True


class RedstoneRepeater(IHorizontalOrientableBlock):
    NAME = "minecraft:repeater"

    DEBUG_WORLD_BLOCK_STATES = PossibleBlockStateBuilder().add_comby("delay", "2", "3", "4").add_comby_side_horizontal("facing").add_comby_bool("locked").add_comby_bool("powered").build()

    def __init__(self):
        super().__init__()
        self.delay = 1
        self.facing = EnumSide.NORTH
        self.locked = False
        self.active = False

    async def on_redstone_update(self):
        pass

    def get_model_state(self) -> dict:
        return {
            "delay": str(self.delay),
            "facing": self.facing.rotate((0, 90, 0)).normal_name,
            "locked": str(self.locked).lower(),
            "powered": str(self.active).lower(),
        }

    async def set_model_state(self, state: dict):
        await super().set_model_state(state)
        self.facing = self.facing.rotate((0, -90, 0))

        if "delay" in state:
            # Clamp the value in case it is out of range
            self.delay = max(min(int(state["delay"]), 4), 1)

        if "locked" in state:
            self.locked = state["locked"] == "true"

        if "powered" in state:
            self.active = state["powered"] == "true"

    def is_connecting_to_redstone(self, side: mcpython.util.enums.EnumSide) -> bool:
        return side == self.facing or side == self.facing.invert()


class RedstoneLamp(AbstractBlock.AbstractBlock):
    DEBUG_WORLD_BLOCK_STATES = [
        {
            "lit": "false"
        },
        {
            "lit": "true",
        }
    ]

    NAME = "minecraft:redstone_lamp"

    def __init__(self):
        super().__init__()
        self.lit = False

    def get_model_state(self) -> dict:
        return {"lit": str(self.lit).lower()}

    async def set_model_state(self, state):
        self.lit = "lit" in state and state["lit"] == "true"

    async def on_redstone_update(self):
        dimension = shared.world.get_dimension_by_name(self.dimension)
        position = self.position

        for face in EnumSide.iterate():
            ask = face.relative_offset(position)
            block = dimension.get_block(ask, none_if_str=True)

            if block is not None and block.get_redstone_output(face.invert()) > 0:
                self.lit = True

                if shared.IS_CLIENT:
                    self.face_info.update(True)

                return

        # todo: this should wait some ticks to be disabled

        self.lit = False

        if shared.IS_CLIENT:
            self.face_info.update(True)
