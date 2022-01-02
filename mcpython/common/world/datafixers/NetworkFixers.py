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

from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer


class AbstractNetworkFixer(ABC):
    BEFORE_VERSION: int = -1
    AFTER_VERSION: int = -1

    @classmethod
    async def apply2stream(
        cls,
        target: IBufferSerializeAble,
        source_buffer: ReadBuffer,
        target_buffer: WriteBuffer,
    ) -> bool:
        """
        Applies this data fixer to a specific object with data
        :param target: the target obj
        :param source_buffer: the source buffer to read from
        :param target_buffer: the buffer to write into, if you want to
        :return: if all data was loaded directly into the block, otherwise, the target_buffer must contain the needed
                 data
        """
        raise NotImplementedError


class BlockDataFixer(AbstractNetworkFixer, ABC):
    """
    Handler for fixing block data using network buffers for blocks
    When subclassing and setting BLOCK_NAME to a good block name (a block name found in registry),
    the fixer will be automatically bound to the block class

    Use the Block.NETWORK_BUFFER_DATA_FIXERS for manual registration

    WARNING: returning True from apply2stream() will intercept any further buffer loading, so also the stuff
             you don't need to do yourself, but instead you use await super().read_from_network_buffer(...)
    """

    BLOCK_NAME: str | typing.List[str] = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.BLOCK_NAME is not None:
            if isinstance(cls.BLOCK_NAME, str):
                shared.registry.get_by_name("minecraft:block")[
                    cls.BLOCK_NAME
                ].NETWORK_BUFFER_DATA_FIXERS[cls.BEFORE_VERSION] = cls
            else:
                for name in cls.BLOCK_NAME:
                    shared.registry.get_by_name("minecraft:block")[
                        name
                    ].NETWORK_BUFFER_DATA_FIXERS[cls.BEFORE_VERSION] = cls

        elif cls.BLOCK_NAME is not None:
            logger.println(
                f"[DFU][WARN] tried to register a data fixer for none-existing block {cls.BLOCK_NAME}"
            )


class ItemDataFixer(AbstractNetworkFixer, ABC):
    """
    Handler for fixing item data using network buffers for items
    When subclassing and setting ITEM_NAME to a good item name (a item name found in registry),
    the fixer will be automatically bound to the block class

    Use the Block.NETWORK_BUFFER_DATA_FIXERS for manual registration

    WARNING: returning True from apply2stream() will intercept any further buffer loading, so also the stuff
             you don't need to do yourself, but instead you use await super().read_from_network_buffer(...)
    """

    ITEM_NAME: str | typing.List[str] = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.ITEM_NAME is not None:
            if isinstance(cls.ITEM_NAME, str):
                shared.registry.get_by_name("minecraft:item")[
                    cls.ITEM_NAME
                ].NETWORK_BUFFER_DATA_FIXERS[cls.BEFORE_VERSION] = cls
            else:
                for name in cls.ITEM_NAME:
                    shared.registry.get_by_name("minecraft:item")[
                        name
                    ].NETWORK_BUFFER_DATA_FIXERS[cls.BEFORE_VERSION] = cls

        elif cls.ITEM_NAME is not None:
            logger.println(
                f"[DFU][WARN] tried to register a data fixer for none-existing item {cls.ITEM_NAME}"
            )


class EntityDataFixer(AbstractNetworkFixer, ABC):
    @classmethod
    def bind(cls, entity_cls):
        entity_cls.DATA_FIXERS[cls.BEFORE_VERSION] = cls


class ChunkInfoMapFixer(AbstractNetworkFixer, ABC):
    """
    Handler for fixing chunk data maps
    """

    MAP_NAME: str = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.MAP_NAME in shared.world_generation_handler.chunk_maps:
            target = shared.world_generation_handler.chunk_maps[cls.MAP_NAME]

            target.DATA_FIXERS[cls.BEFORE_VERSION] = cls

        elif cls.MAP_NAME is not None:
            logger.println(
                f"[DFU][WARN] tried to register a data fixer for a non-existent DataMap named {cls.MAP_NAME}"
            )


class ContainerDataFixer(AbstractNetworkFixer, ABC):
    @classmethod
    def bind(cls, inventory):
        inventory.DATA_FIXERS[cls.BEFORE_VERSION] = cls
