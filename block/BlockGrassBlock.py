"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block


@G.registry
class BlockGrassBlock(Block.Block):
    """
    base class for grass
    todo: add -> dirt convert
    """
    @staticmethod
    def get_name() -> str:
        return "minecraft:grass_block"

    def get_model_state(self) -> dict:
        return {"snowy": "false"}

