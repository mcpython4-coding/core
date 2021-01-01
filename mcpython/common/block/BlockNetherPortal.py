"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.common.block.AbstractBlock
import time
import math


class NetherPortalBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    class for an nether portal
    """

    PORTAL_HOLDING_BLOCKS = ["minecraft:obsidian", "minecraft:nether_portal"]

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
        chunk = G.world.get_dimension_by_name(self.dimension).get_chunk_for_position(
            self.position
        )
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
            chunk = G.world.get_dimension_by_name(
                self.dimension
            ).get_chunk_for_position(position)
        block = chunk.get_block(position)
        if (
            block is None
            or (block.NAME if type(block) != str else block)
            not in self.PORTAL_HOLDING_BLOCKS
        ):
            # print("removing portal as {} does not contain an valid block ({})".format(position, block))
            chunk.remove_block(self.position)
            return True
        return False

    def on_no_collision_collide(self, player, previous: bool):
        if player.should_leave_nether_portal_before_dim_change and not previous:
            player.should_leave_nether_portal_before_dim_change = False
        elif player.should_leave_nether_portal_before_dim_change:
            return
        if player.in_nether_portal_since is None or not previous:
            player.in_nether_portal_since = time.time()
        if time.time() - player.in_nether_portal_since >= 4 or player.gamemode in (
            1,
            3,
        ):
            logger.println(
                "[PORTAL] changing dimension nether <-> overworld... (from: '{}')".format(
                    player.dimension.name
                )
            )
            # todo: create portal on the other side if needed
            # todo: search for portal on other side
            # todo: make it possible for other entities, not only players (-> API change needed!)

            if player.dimension.name == "minecraft:overworld":
                x, y, z = player.position
                player.teleport(
                    (math.floor(x / 8), y, math.floor(z / 8)), "minecraft:the_nether"
                )
            elif player.dimension.name == "minecraft:the_nether":
                x, y, z = player.position
                player.teleport((x * 8, y, z * 8), "minecraft:overworld")
            player.in_nether_portal_since = None


@G.mod_loader("minecraft", "stage:block:load")
def load():
    G.registry.register(NetherPortalBlock)
