"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Block
import util.enums


@G.registry
class BlockGrassBlock(Block.Block):
    """
    base class for grass
    """
    NAME = "minecraft:grass_block"

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
                if blockinst.face_solid[util.enums.EnumSide.UP] or blockinst.face_solid[util.enums.EnumSide.DOWN]:
                    G.world.get_active_dimension().add_block(self.position, "minecraft:dirt")

