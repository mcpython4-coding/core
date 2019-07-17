"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
import globals as G
from . import Block


@G.blockhandler
class BlockBedrock(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:bedrock"

    def get_model_name(self):
        return "block/bedrock"

    def is_brakeable(self) -> bool:
        return False

    @staticmethod
    def is_optainable_by_player() -> bool:
        return False

    @staticmethod
    def is_part_of_pyramids() -> bool:
        return False

