"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import block.Block
import block.BoundingBox
import globals as G
import util.enums


class IWall(block.Block.Block):
    # todo: add bounding-box

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections = {"north": False, "east": False, "south": False, "west": False, "up": False}
        self.on_block_update()

    def get_model_state(self) -> dict:
        state = {key: str(self.connections[key]).lower() for key in self.connections}
        return state

    def on_block_update(self):
        x, y, z = self.position

        block_north: block.Block.Block = G.world.get_active_dimension().get_block((x + 1, y, z))
        block_east: block.Block.Block = G.world.get_active_dimension().get_block((x, y, z + 1))
        block_south: block.Block.Block = G.world.get_active_dimension().get_block((x - 1, y, z))
        block_west: block.Block.Block = G.world.get_active_dimension().get_block((x, y, z - 1))

        self.connections["east"] = block_north is not None and (type(block_north) != str and block_north.is_solid_side(
            util.enums.EnumSide.SOUTH) or issubclass(type(block_north), IWall))
        self.connections["south"] = block_east is not None and (type(block_east) != str and block_east.is_solid_side(
            util.enums.EnumSide.WEST) or issubclass(type(block_east), IWall))
        self.connections["west"] = block_south is not None and (type(block_south) != str and block_south.is_solid_side(
            util.enums.EnumSide.NORTH) or issubclass(type(block_south), IWall))
        self.connections["north"] = block_west is not None and (type(block_west) != str and block_west.is_solid_side(
            util.enums.EnumSide.EAST) or issubclass(type(block_west), IWall))
        self.connections["up"] = False  # for next calculation, this must be False
        self.connections["up"] = list(self.connections.values()).count(True) != 2 or (
            self.connections["north"] != self.connections["south"] or self.connections["east"] !=
            self.connections["west"])
        upper_block: block.Block.Block = G.world.get_active_dimension().get_block((x, y+1, z))
        if not self.connections["up"] and upper_block is not None and type(upper_block) != str and \
                upper_block.is_solid_side(util.enums.EnumSide.DOWN) and not issubclass(type(upper_block), IWall):
            self.connections["up"] = True

    def is_solid_side(self, side) -> bool:
        return False

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
                        for up in range(2):
                            states.append({"north": str(bool(north)).lower(), "east": str(bool(east)).lower(),
                                           "south": str(bool(south)).lower(), "west": str(bool(west)).lower(),
                                           "up": str(bool(up)).lower()})
        return states

# create all classes for the blocks


@G.registry
class AndesiteWall(IWall):
    NAME = "minecraft:andesite_wall"


@G.registry
class BrickWall(IWall):
    NAME = "minecraft:brick_wall"


@G.registry
class CobblestoneWall(IWall):
    NAME = "minecraft:cobblestone_wall"


@G.registry
class DioriteWall(IWall):
    NAME = "minecraft:diorite_wall"


@G.registry
class EndStoneBrickWall(IWall):
    NAME = "minecraft:end_stone_brick_wall"


@G.registry
class GraniteWall(IWall):
    NAME = "minecraft:granite_wall"


@G.registry
class MossyCobblestoneWall(IWall):
    NAME = "minecraft:mossy_cobblestone_wall"


@G.registry
class MossyStoneBrickWall(IWall):
    NAME = "minecraft:mossy_stone_brick_wall"


@G.registry
class NetherBrickWall(IWall):
    NAME = "minecraft:nether_brick_wall"


@G.registry
class PrismarineWall(IWall):
    NAME = "minecraft:prismarine_wall"


@G.registry
class PrismarineWall(IWall):
    NAME = "minecraft:prismarine_wall"


@G.registry
class RedNetherBrickWall(IWall):
    NAME = "minecraft:red_nether_brick_wall"


@G.registry
class RedSandstoneWall(IWall):
    NAME = "minecraft:red_sandstone_wall"


@G.registry
class SandstoneWall(IWall):
    NAME = "minecraft:sandstone_wall"


@G.registry
class StoneBrickWall(IWall):
    NAME = "minecraft:stone_brick_wall"

