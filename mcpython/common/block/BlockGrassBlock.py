"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
from . import AbstractBlock
import mcpython.util.enums


class BlockGrassBlock(AbstractBlock.AbstractBlock):
    """
    base class for grass
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
        for dy in range(y + 1, 256):
            blockinst = G.world.get_active_dimension().get_block((x, dy, z))
            if blockinst is not None:
                break
        else:
            blockinst = G.world.get_active_dimension().get_block((x, y + 1, z))
            if blockinst is not None and type(blockinst) != str:
                if (
                    blockinst.face_solid[mcpython.util.enums.EnumSide.UP]
                    or blockinst.face_solid[mcpython.util.enums.EnumSide.DOWN]
                ):
                    G.world.get_active_dimension().get_chunk_for_position(
                        self.position
                    ).add_block(self.position, "minecraft:dirt")


@G.mod_loader("minecraft", "stage:block:load")
def load():
    G.registry.register(BlockGrassBlock)
