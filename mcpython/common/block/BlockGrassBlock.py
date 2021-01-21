"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from . import AbstractBlock
import mcpython.util.enums


class BlockGrassBlock(AbstractBlock.AbstractBlock):
    """
    Class for the grass block
    """

    NAME = "minecraft:grass_block"

    HARDNESS = 0.5
    BLAST_RESISTANCE = 0.5
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.SHOVEL]

    ENABLE_RANDOM_TICKS = True

    def get_model_state(self) -> dict:
        return {"snowy": "false"}

    def on_random_update(self):
        x, y, z = self.position
        dim = shared.world.get_dimension_by_name(self.dimension)

        for dy in range(y + 1, dim.get_dimension_range()[1] + 1):
            instance = dim.get_block((x, dy, z))
            if instance is not None:
                break

        else:
            instance = dim.get_block((x, y + 1, z))
            if instance is not None and type(instance) != str:
                if (
                    instance.face_solid[mcpython.util.enums.EnumSide.UP]
                    or instance.face_solid[mcpython.util.enums.EnumSide.DOWN]
                ):
                    dim.get_chunk_for_position(self.position).add_block(
                        self.position, "minecraft:dirt"
                    )


@shared.mod_loader("minecraft", "stage:block:load")
def load():
    shared.registry.register(BlockGrassBlock)
