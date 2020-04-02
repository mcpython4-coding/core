"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import block.Block
import block.BoundingBox
import globals as G
import util.enums


class IFence(block.Block.Block):
    """
    Base class for every fence-like block. Expects
    """

    FENCE_TYPE_NAME = set()

    BBOX = None

    # todo: add bounding-box

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections = {"north": False, "east": False, "south": False, "west": False}
        self.on_block_update()
        self.face_solid = {face: False for face in util.enums.EnumSide.iterate()}

    def get_model_state(self) -> dict:
        state = {key: str(self.connections[key]).lower() for key in self.connections}
        return state

    def on_block_update(self):
        x, y, z = self.position

        block_north: block.Block.Block = G.world.get_active_dimension().get_block((x+1, y, z))
        block_east: block.Block.Block = G.world.get_active_dimension().get_block((x, y, z + 1))
        block_south: block.Block.Block = G.world.get_active_dimension().get_block((x - 1, y, z))
        block_west: block.Block.Block = G.world.get_active_dimension().get_block((x, y, z - 1))

        self.connections["east"] = self.connects_to(util.enums.EnumSide.NORTH, block_north)
        self.connections["south"] = self.connects_to(util.enums.EnumSide.EAST, block_east)
        self.connections["west"] = self.connects_to(util.enums.EnumSide.SOUTH, block_south)
        self.connections["north"] = self.connects_to(util.enums.EnumSide.WEST, block_west)

    def set_model_state(self, state: dict):
        for key in state:
            self.connections[key] = state[key] == "true"

    @staticmethod
    def get_all_model_states() -> list:
        states = []
        for north in range(2):
            for east in range(2):
                for south in range(2):
                    for west in range(2):
                        states.append({"north": str(bool(north)).lower(), "east": str(bool(east)).lower(),
                                       "south": str(bool(south)).lower(), "west": str(bool(west)).lower()})
        return states

    def connects_to(self, face: util.enums.EnumSide, blockinstance: block.Block.Block):
        if blockinstance is None or type(blockinstance) == str: return False
        return blockinstance.face_solid[face.invert()] or (
                issubclass(type(blockinstance), IFence) and len(self.FENCE_TYPE_NAME.intersection(
                    blockinstance.FENCE_TYPE_NAME)) > 0)

    BLOCK_ITEM_GENERATOR_STATE = {"east": "true", "west": "true"}


class IWoodenFence(IFence):
    """
    Base class for every wooden fence; used to set the wooden fence flag for all children at ones
    """

    FENCE_TYPE_NAME = {"minecraft:wooden_fence"}


@G.registry
class AcaciaFence(IWoodenFence):
    NAME = "minecraft:acacia_fence"


@G.registry
class BirchFence(IWoodenFence):
    NAME = "minecraft:birch_fence"


@G.registry
class DarkOakFence(IWoodenFence):
    NAME = "minecraft:dark_oak_fence"


@G.registry
class JungleFence(IWoodenFence):
    NAME = "minecraft:jungle_fence"


@G.registry
class OakFence(IWoodenFence):
    NAME = "minecraft:oak_fence"


@G.registry
class SpruceFence(IWoodenFence):
    NAME = "minecraft:spruce_fence"


@G.registry
class NetherBrickFence(IFence):
    NAME = "minecraft:nether_brick_fence"

    FENCE_TYPE_NAME = {"minecraft:nether_fence"}

