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


class IWall(mcpython.common.block.AbstractBlock.AbstractBlock):
    # todo: add bounding-box

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections = {
            "north": False,
            "east": False,
            "south": False,
            "west": False,
            "up": False,
        }
        self.face_solid = {
            face: False for face in mcpython.util.enums.EnumSide.iterate()
        }

    def on_block_added(self):
        if self.NAME in G.modelhandler.blockstates:
            self.on_block_update()

    def get_model_state(self) -> dict:
        state = {
            key: "low" if self.connections[key] else "unset" for key in self.connections
        }
        state["up"] = str(self.connections["up"]).lower()
        return state

    def on_block_update(self):
        x, y, z = self.position

        block_north: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_active_dimension().get_block((x + 1, y, z))
        )
        block_east: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_active_dimension().get_block((x, y, z + 1))
        )
        block_south: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_active_dimension().get_block((x - 1, y, z))
        )
        block_west: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_active_dimension().get_block((x, y, z - 1))
        )

        self.connections["east"] = block_north is not None and (
            type(block_north) != str
            and block_north.face_solid[mcpython.util.enums.EnumSide.SOUTH]
            or issubclass(type(block_north), IWall)
        )
        self.connections["south"] = block_east is not None and (
            type(block_east) != str
            and block_east.face_solid[mcpython.util.enums.EnumSide.WEST]
            or issubclass(type(block_east), IWall)
        )
        self.connections["west"] = block_south is not None and (
            type(block_south) != str
            and block_south.face_solid[mcpython.util.enums.EnumSide.NORTH]
            or issubclass(type(block_south), IWall)
        )
        self.connections["north"] = block_west is not None and (
            type(block_west) != str
            and block_west.face_solid[mcpython.util.enums.EnumSide.EAST]
            or issubclass(type(block_west), IWall)
        )
        self.connections["up"] = False  # for next calculation, this must be False
        self.connections["up"] = list(self.connections.values()).count(True) != 2 or (
            self.connections["north"] != self.connections["south"]
            or self.connections["east"] != self.connections["west"]
        )
        upper_block: mcpython.common.block.AbstractBlock.AbstractBlock = (
            G.world.get_active_dimension().get_block((x, y + 1, z))
        )
        if (
            not self.connections["up"]
            and upper_block is not None
            and type(upper_block) != str
            and upper_block.face_solid[mcpython.util.enums.EnumSide.DOWN]
            and not issubclass(type(upper_block), IWall)
        ):
            self.connections["up"] = True

        self.face_state.update(redraw_complete=True)

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
                            states.append(
                                {
                                    "north": "low" if north else "unset",
                                    "east": "low" if north else "unset",
                                    "south": "low" if north else "unset",
                                    "west": "low" if north else "unset",
                                    "up": str(bool(up)).lower(),
                                }
                            )
        return states


# create all classes for the blocks


class RedSandstoneWall(IWall):
    NAME = "minecraft:red_sandstone_wall"


class SandstoneWall(IWall):
    NAME = "minecraft:sandstone_wall"


@G.modloader("minecraft", "stage:block:load")
def load():
    G.registry.register(RedSandstoneWall)
    G.registry.register(SandstoneWall)