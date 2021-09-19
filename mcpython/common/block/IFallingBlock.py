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
import mcpython.common.block.AbstractBlock
import mcpython.common.event.TickHandler
from mcpython import shared


class IFallingBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    base injection class for falling block
    """

    def __init__(self):
        super().__init__()
        self.fall_cooldown = mcpython.common.event.TickHandler.handler.active_tick - 10

    def on_block_update(self):
        x, y, z = self.position
        dim = shared.world.get_dimension_by_name(self.dimension)
        instance = dim.get_block((x, y - 1, z))
        if not instance:
            shared.entity_manager.spawn_entity(
                "minecraft:falling_block", self.position, representing_block=self
            )
            dim.remove_block(self.position, block_update_self=False)

    def fall(self, check=True):
        x, y, z = self.position
        dim = shared.world.get_dimension_by_name(self.dimension)
        if not check or not dim.get_block((x, y - 1, z)):
            dim.remove_block(self.position)
            dim.check_neighbors(self.position)
            chunk = dim.get_chunk_for_position(self.position)
            chunk.on_block_updated(self.position)
            if y == 0:
                return
            chunk.add_block((x, y - 1, z), self)
            self.on_block_update()
            chunk.check_neighbors(self.position)
