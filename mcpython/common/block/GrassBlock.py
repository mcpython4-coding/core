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
import typing

import mcpython.util.enums
from mcpython import shared
from mcpython.common.item.AbstractToolItem import AbstractToolItem
from mcpython.util.enums import ToolType

from . import IFoliageColoredBlock


class GrassBlock(IFoliageColoredBlock.IFoliageColoredBlock):
    """
    Class for the grass block
    """

    NAME = "minecraft:grass_block"

    HARDNESS = BLAST_RESISTANCE = 0.5
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.SHOVEL}

    ENABLE_RANDOM_TICKS = True

    def get_model_state(self) -> dict:
        return {"snowy": "false"}

    async def on_random_update(self):
        x, y, z = self.position
        dim = shared.world.get_dimension_by_name(self.dimension)

        for dy in range(y + 1, dim.get_world_height_range()[1] + 1):
            instance = dim.get_block((x, dy, z))
            if instance is not None:
                break

        else:
            instance = dim.get_block((x, y + 1, z), none_if_str=True)
            if instance is not None and (instance.face_solid & 3):
                dim.get_chunk_for_position(self.position).add_block(
                    self.position, "minecraft:dirt"
                )

    async def on_player_interaction(
        self,
        player,
        button: int,
        modifiers: int,
        hit_position: tuple,
        itemstack,
    ):
        if (
            itemstack.is_empty()
            or not isinstance(itemstack.item, AbstractToolItem)
            or itemstack.item.TOOL_TYPE != ToolType.SHOVEL
        ):
            return False

        if not itemstack.item.add_damage(1):
            itemstack.clean()

        shared.world.get_dimension_by_name(self.dimension).add_block(
            self.position, "minecraft:dirt_path"
        )
        return True
