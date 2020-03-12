"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import PIL.Image
import event.Registry
import uuid


class Item(event.Registry.IRegistryContent):
    TYPE = "minecraft:item"

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
        self.uuid = uuid.uuid4()

    def get_max_stack_size(self) -> int:  # todo: make attribute
        return 64

    def __eq__(self, other):
        if not issubclass(type(other), Item): return False
        return other.NAME == self.NAME and other.get_data() == self.get_data()

    def on_player_interact(self, player, block, button, modifiers) -> bool:
        """
        called when the player tries to use the item
        :param player: the player interacting
        :param block: the block in focus, may be None
        :param button: the button used
        :param modifiers: the modifiers used
        :return: if default logic should be interrupted
        todo: add an exact_hit-parameter
        """
        return False

    def on_set_from_item(self, block):
        pass

    # functions used by data serializers

    def get_data(self): return "no:data"

    def set_data(self, data): pass

