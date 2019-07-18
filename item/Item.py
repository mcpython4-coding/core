"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import block.Block


class Item:
    @staticmethod
    def get_name() -> str:
        return "minecraft:unknown_item"

    @staticmethod
    def has_block() -> bool:
        return True

    @staticmethod
    def get_item_image_location() -> str:
        raise NotImplementedError()

    def __init__(self):
        pass

    def is_useable_on_block(self, blockinst) -> bool:
        return False

    def on_use_on_block(self, blockinst, triggered_by_item: bool):
        pass

    def get_max_stack_size(self) -> int:
        return 64

