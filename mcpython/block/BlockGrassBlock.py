"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Block
import mcpython.util.enums


@G.registry
class BlockGrassBlock(Block.Block):
    """
    base class for grass
    """
    NAME = "minecraft:grass_block"

    HARDNESS = .5
    BLAST_RESISTANCE = .5
    BEST_TOOLS_TO_BREAK = [mcpython.util.enums.ToolType.SHOVEL]

    ENABLE_RANDOM_TICKS = True

    def get_model_state(self) -> dict:
        return {"snowy": "false"}

    def on_random_update(self):
        x, y, z = self.position
        for dy in range(y+1, 256):
            blockinst = G.world.get_active_dimension().get_block((x, dy, z))
            if blockinst is not None:
                break
        else:
            blockinst = G.world.get_active_dimension().get_block((x, y+1, z))
            if blockinst is not None and type(blockinst) != str:
                if blockinst.face_solid[mcpython.util.enums.EnumSide.UP] or blockinst.face_solid[mcpython.util.enums.EnumSide.DOWN]:
                    G.world.get_active_dimension().get_chunk_for_position(self.position).add_block(
                        self.position, "minecraft:dirt")

