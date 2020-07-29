"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
from . import Block
import mcpython.util.enums


class BlockDirt(Block.Block):
    """
    base class for dirt
    todo: implement -> grass convert
    """

    NAME: str = "minecraft:dirt"

    HARDNESS = .5
    BLAST_RESISTANCE = .5
    BEST_TOOLS_TO_BREAK = [mcpython.util.enums.ToolType.SHOVEL]

    ENABLE_RANDOM_TICKS = True

    def on_random_update(self):
        x, y, z = self.position
        for dy in range(y+1, 256):
            blockinst = G.world.get_active_dimension().get_block((x, dy, z))
            if blockinst is not None:
                break
        else:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    for dz in range(-1, 2):
                        position = (x+dx, y+dy, z+dz)
                        blockinst = G.world.get_active_dimension().get_block(position)
                        if blockinst is not None:
                            if blockinst == "minecraft:grass_block" or (
                                    type(blockinst) != str and blockinst.NAME == "minecraft:grass_block"):
                                G.world.get_active_dimension().get_chunk_for_position(self.position).add_block(
                                    self.position, "minecraft:grass_block")
                                return


@G.modloader("minecraft", "stage:block:load")
def load():
    G.registry.register(BlockDirt)

