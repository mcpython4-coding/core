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
import mcpython.common.block.BoundingBox
from mcpython import shared
import mcpython.util.enums
import mcpython.common.block.PossibleBlockStateBuilder


class AbstractWall(mcpython.common.block.AbstractBlock.AbstractBlock, ABC):
    # todo: add bounding-box

    DEFAULT_FACE_SOLID = (
        mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )

    # todo: up is not always allowed / depends on the configuration of the other stuff!
    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby("north", "low", "unset")
        .add_comby("east", "low", "unset")
        .add_comby("south", "low", "unset")
        .add_comby("west", "low", "unset")
        .add_comby_bool("up")
        .build()
    )

    def __init__(self):
        super().__init__()
        self.connections = {
            "north": False,
            "east": False,
            "south": False,
            "west": False,
            "up": False,
        }

    def on_block_added(self):
        if self.NAME in shared.model_handler.blockstates:
            self.on_block_update()

    def get_model_state(self) -> dict:
        state = {
            key: "low" if self.connections[key] else "unset" for key in self.connections
        }
        state["up"] = str(self.connections["up"]).lower()
        return state

    def on_block_update(self):
        x, y, z = self.position

        dim = shared.world.get_dimension_by_name(self.dimension)

        block_north = dim.get_block((x + 1, y, z), none_if_str=True)
        block_east = dim.get_block((x, y, z + 1), none_if_str=True)
        block_south = dim.get_block((x - 1, y, z), none_if_str=True)
        block_west = dim.get_block((x, y, z - 1), none_if_str=True)

        self.connections["east"] = block_north is not None and (
            block_north.face_solid[mcpython.util.enums.EnumSide.SOUTH]
            or issubclass(type(block_north), AbstractWall)
        )
        self.connections["south"] = block_east is not None and (
            block_east.face_solid[mcpython.util.enums.EnumSide.WEST]
            or issubclass(type(block_east), AbstractWall)
        )
        self.connections["west"] = block_south is not None and (
            block_south.face_solid[mcpython.util.enums.EnumSide.NORTH]
            or issubclass(type(block_south), AbstractWall)
        )
        self.connections["north"] = block_west is not None and (
            block_west.face_solid[mcpython.util.enums.EnumSide.EAST]
            or issubclass(type(block_west), AbstractWall)
        )
        self.connections["up"] = False  # for next calculation, this must be False
        self.connections["up"] = list(self.connections.values()).count(True) != 2 or (
            self.connections["north"] != self.connections["south"]
            or self.connections["east"] != self.connections["west"]
        )
        upper_block = dim.get_block((x, y + 1, z), none_if_str=True)
        if (
            not self.connections["up"]
            and upper_block is not None
            and upper_block.face_solid[mcpython.util.enums.EnumSide.DOWN]
            and not issubclass(type(upper_block), AbstractWall)
        ):
            self.connections["up"] = True

        if shared.IS_CLIENT:
            self.face_state.update(redraw_complete=True)

    def set_model_state(self, state: dict):
        for key in state:
            if key in self.connections:
                self.connections[key] = state[key] in ("low", "true")


def create_wall_class(name: str):
    """
    Constructor helper for creating a new wall class
    For internal usage only!
    """

    class GeneratedWall(AbstractWall):
        NAME = name

    return GeneratedWall


def load():
    shared.registry.register(create_wall_class("minecraft:red_sandstone_wall"))
    shared.registry.register(create_wall_class("minecraft:sandstone_wall"))
