import block.Block
import block.BoundingBox
import globals as G
import util.enums


class IFence(block.Block.Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections = {"north": False, "east": False, "south": False, "west": False}
        self.on_block_update()

    def get_view_bbox(self):
        return block.BoundingBox.FULL_BLOCK_BOUNDING_BOX

    def get_model_state(self) -> dict:
        state = {key: str(self.connections[key]).lower() for key in self.connections}
        return state

    def on_block_update(self):
        print(self.position)

        x, y, z = self.position

        block_north: block.Block.Block = G.world.get_active_dimension().get_block((x+1, y, z))
        block_east: block.Block.Block = G.world.get_active_dimension().get_block((x, y, z + 1))
        block_south: block.Block.Block = G.world.get_active_dimension().get_block((x - 1, y, z))
        block_west: block.Block.Block = G.world.get_active_dimension().get_block((x, y, z - 1))

        self.connections["east"] = block_north is not None and (type(block_north) != str and block_north.is_solid_side(
            util.enums.EnumSide.SOUTH) or issubclass(type(block_north), IFence))
        self.connections["south"] = block_east is not None and (type(block_east) != str and block_east.is_solid_side(
            util.enums.EnumSide.WEST) or issubclass(type(block_east), IFence))
        self.connections["west"] = block_south is not None and (type(block_south) != str and block_south.is_solid_side(
            util.enums.EnumSide.NORTH) or issubclass(type(block_south), IFence))
        self.connections["north"] = block_west is not None and (type(block_west) != str and block_west.is_solid_side(
            util.enums.EnumSide.EAST) or issubclass(type(block_west), IFence))

    def is_solid_side(self, side) -> bool: return False

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


@G.registry
class AcaciaFence(IFence):
    NAME = "minecraft:acacia_fence"


@G.registry
class BirchFence(IFence):
    NAME = "minecraft:birch_fence"


@G.registry
class DarkOakFence(IFence):
    NAME = "minecraft:dark_oak_fence"


@G.registry
class JungleFence(IFence):
    NAME = "minecraft:jungle_fence"


@G.registry
class OakFence(IFence):
    NAME = "minecraft:oak_fence"


@G.registry
class SpruceFence(IFence):
    NAME = "minecraft:spruce_fence"

