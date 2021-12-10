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
import mcpython.util.enums
from mcpython import shared

from . import AbstractBlock


class Dirt(AbstractBlock.AbstractBlock):
    """
    Base class for dirt
    todo: implement real -> grass convert
    """

    NAME: str = "minecraft:dirt"

    HARDNESS = BLAST_RESISTANCE = 0.5
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.SHOVEL}

    ENABLE_RANDOM_TICKS = True

    async def on_random_update(self):
        dim = shared.world.get_dimension_by_name(self.dimension)
        x, y, z = self.position
        for dy in range(y + 1, dim.get_world_height_range()[1] + 1):
            instance = dim.get_block((x, dy, z))
            if instance is not None:
                break

        else:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    for dz in range(-1, 2):
                        position = (x + dx, y + dy, z + dz)
                        instance = dim.get_block(position)
                        if instance is not None:
                            if instance == "minecraft:grass_block" or (
                                type(instance) != str
                                and instance.NAME == "minecraft:grass_block"
                            ):
                                await dim.get_chunk_for_position(self.position).add_block(
                                    self.position, "minecraft:grass_block"
                                )
                                return
