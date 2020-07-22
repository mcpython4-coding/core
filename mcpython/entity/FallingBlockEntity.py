"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import mcpython.entity.Entity
import mcpython.block.Block
import mcpython.util.math
from mcpython.util.enums import EnumSide


@G.registry
class FallingBlock(mcpython.entity.Entity.Entity):
    """
    Class for the falling block entity
    """
    NAME = "minecraft:falling_block"

    def __init__(self, *args, representing_block: mcpython.block.Block.Block = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.block = representing_block  # todo: store in nbt
        self.nbt_data["motion"] = (0, -.4, 0)

    def draw(self):
        if self.block is not None:
            self.block.position = self.position
            G.modelhandler.draw_block(self.block)

    def tick(self):
        super().tick()
        x, y, z = mcpython.util.math.normalize(self.position)
        block = self.chunk.get_block((x, y-1, z))
        if (self.position[1] - y <= .1) and not (block is None or type(block) == str):
            if self.block is None:
                self.kill()
            elif not block.SOLID:
                self.kill()  # todo: drop item in world
            else:
                self.chunk.add_block((x, y, z), self.block)
                self.kill()

    def kill(self, *args, **kwargs):
        super().kill(*args, **kwargs)

