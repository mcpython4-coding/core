"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import PIL.Image
import event.Registry
import uuid
import logger


class Item(event.Registry.IRegistryContent):
    TYPE = "minecraft:item"

    STACK_SIZE = 64
    HAS_BLOCK = True

    @classmethod
    def get_used_texture_files(cls):  # WARNING: will be removed during item rendering update; todo: make attribute
        return [cls.get_default_item_image_location()]

    @staticmethod
    def get_default_item_image_location() -> str:  # WARNING: will be removed during item rendering update
        raise NotImplementedError()

    def __init__(self):
        self.uuid = uuid.uuid4()

    def __eq__(self, other):
        if not issubclass(type(other), Item): return False
        return other.NAME == self.NAME and other.get_data() == self.get_data()

    # default getter functions

    def get_active_image_location(self):  # WARNING: will be removed during item rendering update
        return self.get_default_item_image_location()

    def get_block(self) -> str:
        return self.NAME

    # events

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

    def set_data(self, data):
        if data != "no:data":
            logger.println("[WARNING] data-deserialization did NOT expect data, but data '{}' was got".format(data))

