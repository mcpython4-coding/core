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
from mcpython import shared
from . import AbstractBlock
import mcpython.util.enums


class BlockDirt(AbstractBlock.AbstractBlock):
    """
    Base class for dirt
    todo: implement real -> grass convert
    """

    NAME: str = "minecraft:dirt"

    HARDNESS = 0.5
    BLAST_RESISTANCE = 0.5
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.SHOVEL]

    ENABLE_RANDOM_TICKS = True

    def on_random_update(self):
        dim = shared.world.get_dimension_by_name(self.dimension)
        x, y, z = self.position
        for dy in range(y + 1, dim.get_dimension_range()[1] + 1):
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
                                dim.get_chunk_for_position(self.position).add_block(
                                    self.position, "minecraft:grass_block"
                                )
                                return


@shared.mod_loader("minecraft", "stage:block:load")
def load():
    shared.registry.register(BlockDirt)
