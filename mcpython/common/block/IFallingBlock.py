"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.common.block.Block
import mcpython.common.event.TickHandler
import mcpython.common.event.TickHandler


class IFallingBlock(mcpython.common.block.Block.Block):
    """
    base injection class for falling block
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fall_cooldown = mcpython.common.event.TickHandler.handler.active_tick - 10

    def on_block_update(self):
        x, y, z = self.position
        blockinst = G.world.get_active_dimension().get_block((x, y - 1, z))
        if not blockinst:
            G.entityhandler.add_entity(
                "minecraft:falling_block", self.position, representing_block=self
            )
            G.world.get_active_dimension().remove_block(self.position)

    def fall(self, check=True):
        x, y, z = self.position
        if not check or not G.world.get_active_dimension().get_block((x, y - 1, z)):
            G.world.get_active_dimension().remove_block(
                self.position, blockupdateself=False
            )
            G.world.get_active_dimension().check_neighbors(self.position)
            chunk = G.world.get_active_dimension().get_chunk_for_position(self.position)
            chunk.on_block_updated(self.position)
            if y == 0:
                return
            chunk.add_block((x, y - 1, z), self, blockupdateself=False)
            self.on_block_update()
            chunk.check_neighbors(self.position)
