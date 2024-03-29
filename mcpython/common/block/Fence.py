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
from abc import ABC

import mcpython.common.block.AbstractBlock
import mcpython.common.block.PossibleBlockStateBuilder
import mcpython.engine.physics.AxisAlignedBoundingBox
import mcpython.util.enums
from mcpython import shared
from mcpython.engine import logger
from mcpython.util.enums import EnumSide


# todo: add factory method for this
class AbstractFence(mcpython.common.block.AbstractBlock.AbstractBlock, ABC):
    """
    Abstract base class for every fence-like block
    """

    # The type list of the fences; same types are able to connect to each other, not same types not
    FENCE_TYPE_NAME = set()

    # the bounding box todo: add the real bounding box
    BBOX = None

    # the debug world states, constructed by a builder, using all possible combinations
    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .combinations()
        .add_comby_bool("north")
        .add_comby_bool("east")
        .add_comby_bool("south")
        .add_comby_bool("west")
        .build()
    )

    HARDNESS = 2
    BLAST_RESISTANCE = 3

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

    def __init__(self):
        super().__init__()
        self.connections = {
            "north": False,
            "east": False,
            "south": False,
            "west": False,
        }

    async def on_block_added(self):
        # On dedicated servers, we don't have the blockstate lookup
        # todo: cache the lookup beforehand!
        if not shared.IS_CLIENT or self.NAME in shared.model_handler.blockstates:
            await self.on_block_update()

    def get_model_state(self) -> dict:
        state = {key: str(self.connections[key]).lower() for key in self.connections}
        return state

    async def on_block_update(self):
        x, y, z = self.position

        block_north: mcpython.common.block.AbstractBlock.AbstractBlock = (
            shared.world.get_dimension_by_name(self.dimension).get_block((x + 1, y, z))
        )
        block_east: mcpython.common.block.AbstractBlock.AbstractBlock = (
            shared.world.get_dimension_by_name(self.dimension).get_block((x, y, z + 1))
        )
        block_south: mcpython.common.block.AbstractBlock.AbstractBlock = (
            shared.world.get_dimension_by_name(self.dimension).get_block((x - 1, y, z))
        )
        block_west: mcpython.common.block.AbstractBlock.AbstractBlock = (
            shared.world.get_dimension_by_name(self.dimension).get_block((x, y, z - 1))
        )

        self.connections["east"] = self.connects_to(
            mcpython.util.enums.EnumSide.NORTH, block_north
        )
        self.connections["south"] = self.connects_to(
            mcpython.util.enums.EnumSide.EAST, block_east
        )
        self.connections["west"] = self.connects_to(
            mcpython.util.enums.EnumSide.SOUTH, block_south
        )
        self.connections["north"] = self.connects_to(
            mcpython.util.enums.EnumSide.WEST, block_west
        )

        if shared.IS_CLIENT:
            self.face_info.update(redraw_complete=True)

        await self.schedule_network_update()

    async def set_model_state(self, state: dict):
        for key in state:
            self.connections[key] = state[key] == "true"

    def connects_to(
        self,
        face: mcpython.util.enums.EnumSide,
        instance: mcpython.common.block.AbstractBlock.AbstractBlock,
    ):
        if instance is None or type(instance) == str:
            return False

        return instance.face_solid & face.invert().bitflag or (
            issubclass(type(instance), AbstractFence)
            and len(self.FENCE_TYPE_NAME.intersection(instance.FENCE_TYPE_NAME)) > 0
        )

    # the state the block item generator should use, this kinda looks nice
    BLOCK_ITEM_GENERATOR_STATE = {"east": "true", "west": "true"}


class AbstractFenceGate(mcpython.common.block.AbstractBlock.AbstractBlock, ABC):
    """
    todo: implement behaviour
    """

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .combinations()
        .add_comby_side_horizontal("facing")
        .add_comby_bool("in_wall")
        .add_comby_bool("open")
        .build()
    )

    def __init__(self):
        super().__init__()
        self.facing = EnumSide.NORTH
        self.in_wall = False
        self.open = False

    def get_model_state(self) -> dict:
        return {
            "facing": self.facing.normal_name,
            "in_wall": str(self.in_wall).lower(),
            "open": str(self.open).lower(),
        }

    async def set_model_state(self, state: dict):
        if "facing" in state:
            try:
                self.facing = EnumSide[state["facing"].upper()]
            except KeyError:
                logger.println(
                    f"[FATAL][WARN] {self} got unexpected data for facing: {repr(state['facing'])}"
                )

        if "in_wall" in state:
            self.in_wall = state["in_wall"] == "true"

        if "open" in state:
            self.open = state["open"] == "true"

    BLOCK_ITEM_GENERATOR_STATE = {
        "facing": "north",
        "in_wall": "false",
        "opened": "true",
    }


class AbstractWoodenFence(AbstractFence):
    """
    Base class for every wooden fence; used to set the wooden fence flag for all children at ones
    """

    FENCE_TYPE_NAME = {"minecraft:wooden_fence"}


class BirchFence(AbstractWoodenFence):
    NAME = "minecraft:birch_fence"


class DarkOakFence(AbstractWoodenFence):
    NAME = "minecraft:dark_oak_fence"


class JungleFence(AbstractWoodenFence):
    NAME = "minecraft:jungle_fence"


class OakFence(AbstractWoodenFence):
    NAME = "minecraft:oak_fence"


class SpruceFence(AbstractWoodenFence):
    NAME = "minecraft:spruce_fence"


class AcaciaFence(AbstractWoodenFence):
    NAME = "minecraft:acacia_fence"


class CrimsonFence(AbstractFence):
    FENCE_TYPE_NAME = {"minecraft:wooden_fence", "minecraft:nether_fence"}

    NAME = "minecraft:crimson_fence"


class WarpedFence(AbstractFence):
    FENCE_TYPE_NAME = {"minecraft:wooden_fence", "minecraft:nether_fence"}

    NAME = "minecraft:warped_fence"


class NetherBrickFence(AbstractFence):
    NAME = "minecraft:nether_brick_fence"

    FENCE_TYPE_NAME = {"minecraft:nether_fence"}
