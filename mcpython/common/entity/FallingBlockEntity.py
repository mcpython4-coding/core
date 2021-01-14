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
import mcpython.common.entity.AbstractEntity
import mcpython.common.block.AbstractBlock
import mcpython.util.math


@G.registry
class FallingBlockEntity(mcpython.common.entity.AbstractEntity.AbstractEntity):
    """
    Class for the falling block entity

    todo: can we replicate some original block behaviour, like inventories, interaction, ...?
    """

    NAME = "minecraft:falling_block"

    def __init__(
        self,
        *args,
        representing_block: mcpython.common.block.AbstractBlock.AbstractBlock = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.block = representing_block  # todo: store in nbt
        self.nbt_data["motion"] = (0, -0.4, 0)

    def draw(self):
        if self.block is not None:
            self.block.position = self.position
            G.model_handler.draw_block(self.block)  # todo: use batch

    def tick(self, dt):
        super().tick(dt)

        if self.block is None:
            self.kill()
            return

        x, y, z = mcpython.util.math.normalize(self.position)
        block = self.chunk.get_block((x, y - 1, z))
        if (self.position[1] - y <= 0.1) and not (block is None or type(block) == str):
            if not block.IS_SOLID:
                self.kill()  # todo: drop item in world
            else:
                self.chunk.add_block((x, y, z), self.block)
                self.kill()
