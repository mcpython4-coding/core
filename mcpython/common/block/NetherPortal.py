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

import mcpython.common.block.AbstractBlock
from mcpython import shared
from mcpython.engine import logger


class NetherPortalBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    Class for the nether portal block
    Uses the entity no collision collide system
    """

    NAME = "minecraft:nether_portal"

    NO_COLLISION = True
    SOLID = False

    HARDNESS = -1

    DEFAULT_FACE_SOLID = (
        mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )

    def __init__(self):
        super().__init__()
        self.axis = "x"

    def get_model_state(self) -> dict:
        return {"axis": self.axis}

    def set_model_state(self, state: dict):
        self.axis = state.setdefault("axis", "x")

    DEBUG_WORLD_BLOCK_STATES = [{"axis": "x"}, {"axis": "z"}]

    def on_block_update(self):
        self.on_redstone_update()
        self.check_valid_surrounding()

    def check_valid_surrounding(self):
        x, y, z = self.position
        chunk = shared.world.get_dimension_by_name(
            self.dimension
        ).get_chunk_for_position(self.position)

        if self.check_valid_block((x, y + 1, z), chunk):
            return

        if self.check_valid_block((x, y - 1, z), chunk):
            return

        if self.axis == "x":
            if self.check_valid_block((x + 1, y, z)):
                return
            if self.check_valid_block((x - 1, y, z)):
                return

        elif self.axis == "z":
            if self.check_valid_block((x, y, z + 1)):
                return
            if self.check_valid_block((x, y, z - 1)):
                return

    def check_valid_block(self, position: tuple, chunk=None):
        if chunk is None:
            chunk = shared.world.get_dimension_by_name(
                self.dimension
            ).get_chunk_for_position(position)

        block = chunk.get_block(position, none_if_str=True)

        if block is None or "#minecraft:supports_nether_portal" not in block.TAGS:
            chunk.remove_block(self.position)
            return True

        return False

    def on_no_collision_collide(self, entity, previous: bool):
        if entity.should_leave_nether_portal_before_dim_change:
            if not previous:
                entity.should_leave_nether_portal_before_dim_change = False
            else:
                return

        if entity.in_nether_portal_since is None or not previous:
            entity.in_nether_portal_since = time.time()

        if time.time() - entity.in_nether_portal_since >= 4 or entity.gamemode in (
            1,
            3,
        ):
            logger.println(
                "[PORTAL] changing dimension nether <-> overworld... (from '{}'-dimension)".format(
                    entity.dimension.get_name()
                )
            )
            # todo: create portal on the other side if needed
            # todo: search for portal on other side
            # todo: make it possible for other entities, not only players (-> API change needed!)
            # todo: add dimension tags for defining this factors, and move teleport code out of here!

            if entity.dimension.name == "minecraft:overworld":
                x, y, z = entity.position
                entity.teleport(
                    (math.floor(x / 8), y, math.floor(z / 8)), "minecraft:the_nether"
                )

            elif entity.dimension.name == "minecraft:the_nether":
                x, y, z = entity.position
                entity.teleport((x * 8, y, z * 8), "minecraft:overworld")

            entity.in_nether_portal_since = None
