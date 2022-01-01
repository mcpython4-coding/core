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
import typing
from abc import ABC

import mcpython.common.event.api
import mcpython.common.event.Registry
from mcpython.common.capability.ICapabilityContainer import ICapabilityContainer
from mcpython.common.world.datafixers.NetworkFixers import ItemDataFixer
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer


class AbstractItem(
    mcpython.common.event.api.IRegistryContent,
    ICapabilityContainer,
    IBufferSerializeAble,
    ABC,
):
    VERSION = 0
    NETWORK_BUFFER_DATA_FIXERS: typing.Dict[int, ItemDataFixer] = {}

    TYPE = "minecraft:item"
    CAPABILITY_CONTAINER_NAME = "minecraft:item"

    STACK_SIZE = 64
    HAS_BLOCK = True
    ITEM_NAME_COLOR = "white"

    # Attribute storing an AbstractItemRenderer instance for rendering this item
    # May only be set on client due to loading pyglet
    BOUND_ITEM_RENDERER = None

    @classmethod
    def get_used_texture_files(
        cls,
    ):  # WARNING: will be removed during item rendering update; todo: make attribute
        return [cls.get_default_item_image_location()]

    @classmethod
    def get_default_item_image_location(
        cls,
    ) -> str:  # WARNING: will be removed during item rendering update
        return "assets/{}/textures/item/{}.png".format(*cls.NAME.split(":"))

    def __init__(self):
        super().__init__()

        self.stored_block_state = None
        self.can_destroy = None
        self.can_be_set_on = None

    def draw_in_inventory(
        self, itemstack, position: typing.Tuple[int, int], scale: float
    ):
        pass

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        version = buffer.read_uint()

        if version != self.VERSION:
            while version in self.NETWORK_BUFFER_DATA_FIXERS and version != self.VERSION:
                fixer = self.NETWORK_BUFFER_DATA_FIXERS[version]

                write = WriteBuffer()

                try:
                    if await fixer.apply2stream(self, buffer, write) is True:
                        break
                except:
                    logger.print_exception(
                        f"during applying data fixer to item {self.NAME}; discarding data"
                    )
                    return

                buffer = ReadBuffer(write.get_data())
                version = fixer.AFTER_VERSION

        await super(ICapabilityContainer, self).read_from_network_buffer(buffer)
        can_destroy_flag = buffer.read_bool()
        can_be_set_on_flag = buffer.read_bool()

        if can_destroy_flag:
            self.can_destroy = await buffer.collect_list(buffer.read_string)

        if can_be_set_on_flag:
            self.can_be_set_on = await buffer.collect_list(buffer.read_string)

    async def read_internal_for_migration(self, buffer: ReadBuffer):
        await super(ICapabilityContainer, self).read_from_network_buffer(buffer)
        can_destroy_flag = buffer.read_bool()
        can_be_set_on_flag = buffer.read_bool()

        if can_destroy_flag:
            self.can_destroy = await buffer.collect_list(buffer.read_string)

        if can_be_set_on_flag:
            self.can_be_set_on = await buffer.collect_list(buffer.read_string)

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_uint(self.VERSION)

        await super(ICapabilityContainer, self).write_to_network_buffer(buffer)
        can_destroy_flag = self.can_destroy is not None
        can_be_set_on_flag = self.can_be_set_on is not None

        buffer.write_bool(can_destroy_flag)
        buffer.write_bool(can_be_set_on_flag)

        if can_destroy_flag:
            await buffer.write_list(self.can_destroy, lambda e: buffer.write_string(e))

        if can_be_set_on_flag:
            await buffer.write_list(
                self.can_be_set_on, lambda e: buffer.write_string(e)
            )

    async def write_internal_for_migration(self, buffer: WriteBuffer):
        await super(ICapabilityContainer, self).write_to_network_buffer(buffer)
        can_destroy_flag = self.can_destroy is not None
        can_be_set_on_flag = self.can_be_set_on is not None

        buffer.write_bool(can_destroy_flag)
        buffer.write_bool(can_be_set_on_flag)

        if can_destroy_flag:
            await buffer.write_list(self.can_destroy, lambda e: buffer.write_string(e))

        if can_be_set_on_flag:
            await buffer.write_list(
                self.can_be_set_on, lambda e: buffer.write_string(e)
            )

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
        return other.NAME == self.NAME

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

    async def on_player_interact(
        self, player, block, button: int, modifiers: int, itemstack, previous
    ) -> bool:
        """
        Called when the player tries to use the item by pressing a mouse button
        :param player: the player interacting
        :param block: the block in focus, may be None if no block is in range
        :param button: the button used
        :param modifiers: the modifiers used
        :param itemstack: the itemstack used
        :param previous: the precious block position hit with, or None if no block was hit
        :return: if default logic should be interrupted
        todo: pass full hit info into here
        """
        return False

    async def on_block_broken_with(self, itemstack, player, block):
        pass

    async def on_set_from_item(self, block):
        if self.stored_block_state is not None and self.NAME == block.NAME:
            await block.set_item_saved_state(self.stored_block_state)

    def get_tooltip_provider(self):
        import mcpython.client.gui.HoveringItemBox

        return mcpython.client.gui.HoveringItemBox.DEFAULT_ITEM_TOOLTIP

    def get_additional_tooltip_text(self, stack, renderer) -> list:
        return []
