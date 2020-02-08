"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Block


@G.registry
class BlockDirt(Block.Block):
    """
    base class for dirt
    todo: implement -> grass convert
    """

    @staticmethod
    def get_name() -> str:
        return "minecraft:dirt"

    def on_random_update(self):
        x, y, z = self.position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    position = (x+dx, y+dy, z+dz)
                    blockinst = G.world.get_active_dimension().get_block(position)
                    if blockinst is not None:
                        if blockinst == "minecraft:grass_block" or (
                                type(blockinst) != str and blockinst.get_name() == "minecraft:grass_block"):
                            G.world.get_active_dimension().add_block(self.position, "minecraft:grass_block")
                            return

