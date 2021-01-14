"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.common.block.AbstractBlock
import mcpython.common.event.TickHandler
import mcpython.common.event.TickHandler


class IFallingBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    base injection class for falling block
    """

    def __init__(self):
        super().__init__()
        self.fall_cooldown = mcpython.common.event.TickHandler.handler.active_tick - 10

    def on_block_update(self):
        x, y, z = self.position
        dim = G.world.get_dimension_by_name(self.dimension)
        instance = dim.get_block((x, y - 1, z))
        if not instance:
            G.entity_handler.spawn_entity(
                "minecraft:falling_block", self.position, representing_block=self
            )
            dim.remove_block(self.position)

    def fall(self, check=True):
        x, y, z = self.position
        dim = G.world.get_dimension_by_name(self.dimension)
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
