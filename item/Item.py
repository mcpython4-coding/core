"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import PIL.Image


class Item:
    @staticmethod
    def get_name() -> str:
        return "minecraft:unknown_item"

    @staticmethod
    def has_block() -> bool:
        return True

    def get_block(self) -> str:
        return self.get_name()

    @staticmethod
    def get_item_image_location() -> str:
        raise NotImplementedError()

    @staticmethod
    def get_as_item_image(image: PIL.Image.Image) -> PIL.Image.Image: return image.resize((32, 32))

    def __init__(self):
        pass

    def is_useable_on_block(self, blockinst) -> bool:
        return False

    def on_use_on_block(self, blockinst, triggered_by_item: bool):
        pass

    def get_max_stack_size(self) -> int:
        return 64

    def __eq__(self, other):
        if not issubclass(type(other), Item): return False
        return other.get_name() == self.get_name()

