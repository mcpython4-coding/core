"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
from util.math import tex_coords


class Block:
    def __init__(self, position):
        self.position = position
        self.on_create()

    @staticmethod
    def get_name() -> str:
        return "minecraft:missing_name"

    def on_create(self):
        pass

    def on_delete(self):
        pass

    def get_model_name(self):
        return None

    def is_brakeable(self) -> bool:
        return True

    @staticmethod
    def is_optainable_by_player() -> bool:
        return True

    @staticmethod
    def is_part_of_pyramids() -> bool:
        return True

    def on_random_update(self):
        pass

    def on_block_update(self):
        pass

