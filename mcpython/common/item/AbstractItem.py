"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
import mcpython.common.event.Registry


class AbstractItem(mcpython.common.event.Registry.IRegistryContent):
    TYPE = "minecraft:item"

    STACK_SIZE = 64
    HAS_BLOCK = True
    ITEM_NAME_COLOR = "white"

    @classmethod
    def get_used_texture_files(
        cls,
    ):  # WARNING: will be removed during item rendering update; todo: make attribute
        return [cls.get_default_item_image_location()]

    @staticmethod
    def get_default_item_image_location() -> str:  # WARNING: will be removed during item rendering update
        raise NotImplementedError()

    def __init__(self):
        self.stored_block_state = None
        self.can_destroy = None
        self.can_be_set_on = None

    def check_can_be_set_on(self, block, player):
        return player.gamemode != 2 or (
            self.can_be_set_on is not None and block.NAME in self.can_be_set_on
        )

    def check_can_destroy(self, block, player):
        return player.gamemode != 2 or (
            self.can_destroy is not None and block.NAME in self.can_destroy
        )

    def __eq__(self, other):
        if not issubclass(type(other), AbstractItem):
            return False
        return other.NAME == self.NAME and other.get_data() == self.get_data()

    def on_clean(self, itemstack):
        pass

    def on_copy(self, old_itemstack, new_itemstack):
        pass

    # default getter functions

    def get_active_image_location(
        self,
    ):  # WARNING: will be removed during item rendering update
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

    def on_block_broken_with(self, itemstack, player, block):
        pass

    def on_set_from_item(self, block):
        if self.stored_block_state is not None and self.NAME == block.NAME:
            block.set_item_saved_state(self.stored_block_state)

    # functions used by data serializers

    def get_data(self):
        return self.stored_block_state, self.can_destroy, self.can_be_set_on

    def set_data(self, data):
        if data == "no:data":
            return
        self.stored_block_state, self.can_destroy, self.can_be_set_on = data

    def get_tooltip_provider(self):
        import mcpython.client.gui.HoveringItemBox

        return mcpython.client.gui.HoveringItemBox.DEFAULT_ITEM_TOOLTIP

    def get_additional_tooltip_text(self, stack, renderer) -> list:
        return []
