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
from mcpython import shared
from mcpython.common.config import ADVANCED_FACES
from mcpython.util.math import normalize


def collide(position: tuple, height: int, previous=None):
    """
    Checks to see if the player at the given `position` and `height`
    is colliding with any blocks in the world.

    :param position: The (x, y, z) position to check for collisions at.
    :param height: The height of the player.
    :param previous: the previous position the player was, for the block collision API, optional
    :return The new position of the player taking into account collisions.

    todo: make player based
    todo: make account player & block hit box
    """
    dimension = shared.world.get_active_dimension()
    player = shared.world.get_active_player()

    previous_positions = (
        sum(get_colliding_blocks(previous, height), []) if previous is not None else []
    )
    # How much overlap with a dimension of a surrounding block you need to
    # have to count as a collision. If 0, touching terrain at all counts as
    # a collision. If .49, you sink into the ground, as if walking through
    # tall grass. If >= .5, you'll fall through the ground.
    pad = 0.1
    p = list(position)
    np = normalize(position)
    for face in ADVANCED_FACES:  # check all surrounding blocks
        for i in range(3):  # check each dimension independently
            if not face[i]:
                continue
            # How much overlap you have with this dimension.
            d = (p[i] - np[i]) * face[i]
            if d < pad:
                continue

            for dy in range(height):  # check each height
                op = list(np)
                op[1] -= dy
                op[i] += face[i]
                chunk = dimension.get_chunk_for_position(tuple(op), generate=False)
                block = chunk.get_block(tuple(op))
                blockstate = block is not None

                if not chunk.generated:
                    if shared.world.config["enable_world_barrier"]:
                        blockstate = True

                if not blockstate:
                    continue

                if (
                    block is not None
                    and type(block) != str
                    and block.NO_ENTITY_COLLISION
                ):
                    block.on_no_collision_collide(
                        player,
                        block.position in previous_positions,
                    )
                    continue

                p[i] -= (d - pad) * face[i]
                if face == (0, -1, 0) or face == (0, 1, 0):
                    # You are colliding with the ground or ceiling, so stop
                    # falling / rising.

                    # todo: move to player
                    if shared.IS_CLIENT:
                        shared.window.dy = 0

                if face == (0, -1, 0):
                    player.flying = False
                    if player.gamemode in (0, 2) and player.fallen_since_y is not None:
                        dy = player.fallen_since_y - player.position[1] - 3

                        if (
                            dy > 0
                            and shared.world.gamerule_handler.table[
                                "fallDamage"
                            ].status.status
                        ):
                            player.damage(dy)

                        player.fallen_since_y = None
                break

    return tuple(p)


def get_colliding_blocks(position: tuple, height: int) -> tuple:
    """
    Similar to collide(), but will simply return an list of block-positions the player collides with and an list of blocks the player is in, but should not collide
    :param position: the position to use as center
    :param height: the height of the player
    :return: a tuple of colliding full blocks and colliding no collision blocks
    """
    positions_colliding = []
    positions_no_colliding = []
    pad = 0.1
    p = list(position)
    np = normalize(position)
    dimension = shared.world.get_active_dimension()

    for face in ADVANCED_FACES:  # check all surrounding blocks
        for i in range(3):  # check each dimension independently
            if not face[i]:
                continue

            # How much overlap you have with this dimension.
            d = (p[i] - np[i]) * face[i]
            if d < pad:
                continue

            for dy in range(height):  # check each height
                op = list(np)
                op[1] -= dy
                op[i] += face[i]
                chunk = dimension.get_chunk_for_position(tuple(op), generate=False)
                block = chunk.get_block(tuple(op))
                if block is None:
                    continue

                if type(block) != str and block.NO_ENTITY_COLLISION:
                    positions_no_colliding.append(block.position)
                    continue

                p[i] -= (d - pad) * face[i]
                positions_colliding.append(block.position)
                break

    return positions_colliding, positions_no_colliding
