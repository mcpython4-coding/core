"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.block.AbstractBlock
import mcpython.common.block.BoundingBox
from mcpython import shared as G
import mcpython.util.enums


class IFence(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    Base class for every fence-like block. Expects
    """

    FENCE_TYPE_NAME: set = set()  # the type list of the fences

    # todo: add bounding-box
    BBOX = None  # the bounding box

    DEBUG_WORLD_BLOCK_STATES = []
    for north in range(2):
        for east in range(2):
            for south in range(2):
                for west in range(2):
                    DEBUG_WORLD_BLOCK_STATES.append(
                        {
                            "north": str(bool(north)).lower(),
                            "east": str(bool(east)).lower(),
                            "south": str(bool(south)).lower(),
                            "west": str(bool(west)).lower(),
                        }
                    )

    DEFAULT_FACE_SOLID = (
        mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )

    def __init__(self, *args, **kwargs):
        """
        will create the fence
        """
        super().__init__(*args, **kwargs)
        self.connections = {
            "north": False,
            "east": False,
            "south": False,
            "west": False,
        }

    def on_block_added(self):
        if self.NAME in G.model_handler.blockstates:
            self.on_block_update()

    def get_model_state(self) -> dict:
        state = {key: str(self.connections[key]).lower() for key in self.connections}
        return state

    def on_block_update(self):
        x, y, z = self.position

        block_north: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_dimension_by_name(self.dimension).get_block((x + 1, y, z))
        )
        block_east: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_dimension_by_name(self.dimension).get_block((x, y, z + 1))
        )
        block_south: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_dimension_by_name(self.dimension).get_block((x - 1, y, z))
        )
        block_west: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_dimension_by_name(self.dimension).get_block((x, y, z - 1))
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

        self.face_state.update(redraw_complete=True)

    def set_model_state(self, state: dict):
        for key in state:
            self.connections[key] = state[key] == "true"

    def connects_to(
        self,
        face: mcpython.util.enums.EnumSide,
        blockinstance: mcpython.common.block.AbstractBlock.AbstractBlock,
    ):
        if blockinstance is None or type(blockinstance) == str:
            return False
        return blockinstance.face_solid[face.invert()] or (
            issubclass(type(blockinstance), IFence)
            and len(self.FENCE_TYPE_NAME.intersection(blockinstance.FENCE_TYPE_NAME))
            > 0
        )

    BLOCK_ITEM_GENERATOR_STATE = {"east": "true", "west": "true"}


class IWoodenFence(IFence):
    """
    Base class for every wooden fence; used to set the wooden fence flag for all children at ones
    """

    FENCE_TYPE_NAME = {"minecraft:wooden_fence"}


class AcaciaFence(IWoodenFence):
    NAME = "minecraft:acacia_fence"


class BirchFence(IWoodenFence):
    NAME = "minecraft:birch_fence"


class DarkOakFence(IWoodenFence):
    NAME = "minecraft:dark_oak_fence"


class JungleFence(IWoodenFence):
    NAME = "minecraft:jungle_fence"


class OakFence(IWoodenFence):
    NAME = "minecraft:oak_fence"


class SpruceFence(IWoodenFence):
    NAME = "minecraft:spruce_fence"


class CrimsonFence(IFence):
    FENCE_TYPE_NAME = {"minecraft:wooden_fence", "minecraft:nether_fence"}

    NAME = "minecraft:crimson_fence"


class WarpedFence(IFence):
    FENCE_TYPE_NAME = {"minecraft:wooden_fence", "minecraft:nether_fence"}

    NAME = "minecraft:warped_fence"


class NetherBrickFence(IFence):
    NAME = "minecraft:nether_brick_fence"

    FENCE_TYPE_NAME = {"minecraft:nether_fence"}


@G.mod_loader("minecraft", "stage:block:load")
def load():
    G.registry.register(OakFence)
    G.registry.register(SpruceFence)
    G.registry.register(DarkOakFence)
    G.registry.register(JungleFence)
    G.registry.register(BirchFence)
    G.registry.register(AcaciaFence)
    G.registry.register(WarpedFence)
    G.registry.register(CrimsonFence)
    G.registry.register(NetherBrickFence)
