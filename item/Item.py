"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import PIL.Image


class Item:
    NAME = "minecraft:unknown_item"

    @classmethod
    def get_used_texture_files(cls):
        return [cls.get_default_item_image_location()]

    @classmethod
    def get_name(cls) -> str: return cls.NAME

    @staticmethod
    def has_block() -> bool:
        return True

    def get_block(self) -> str:
        return self.NAME

    @staticmethod
    def get_default_item_image_location() -> str:
        raise NotImplementedError()

    def get_active_image_location(self):
        return self.get_default_item_image_location()

    def __init__(self):
        pass

    def get_max_stack_size(self) -> int:
        return 64

    def __eq__(self, other):
        if not issubclass(type(other), Item): return False
        return other.NAME == self.NAME and other.get_data() == self.get_data()

    def on_player_interact(self, block, button, modifiers) -> bool:
        return False

    def on_set_from_item(self, block):
        pass

    def get_data(self) -> dict: return {}

