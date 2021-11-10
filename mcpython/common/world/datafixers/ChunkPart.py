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

from mcpython.common.world.serializer.util import access_region_data, write_region_data

from .IDataFixer import IPartFixer


class BlockPartFixer(IPartFixer):
    """
    Fixer for fixing special block data
    Applied only ONES per block-palette entry, not ones per block. Will change all blocks of the same kind
    in that chunk
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    TARGET_BLOCK_NAME = None  # on which block(s) to apply

    @classmethod
    async def fix(
        cls,
        save_file,
        dimension: int,
        region,
        chunk: typing.Tuple[int, int],
        data,
    ) -> dict:
        """
        called to apply the fix
        :param save_file: the save-file-instance to use
        :param dimension: the dim in
        :param region: the region in
        :param chunk: the chunk in
        :param data: the block data
        :return: the transformed data
        """

    @classmethod
    async def apply(cls, save_file, *args, **kwargs):
        blocks = (
            cls.TARGET_BLOCK_NAME
            if type(cls.TARGET_BLOCK_NAME) in (list, tuple, set)
            else (cls.TARGET_BLOCK_NAME,)
        )
        for dim, region in save_file.region_iterator():
            data = await access_region_data(save_file, dim, region)
            if data is None:
                continue
            for chunk in data:
                if chunk == "version":
                    continue
                palette = data[chunk]["block_palette"]
                for i, entry in enumerate(palette):
                    if entry["name"] in blocks:
                        palette[i] = await cls.fix(save_file, dim, region, chunk, entry)
            await write_region_data(save_file, dim, region, data)


class ChunkDataFixer(IPartFixer):
    """
    Fixer targeting an whole chunk-data dict
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    async def fix(
        cls,
        save_file,
        dimension: int,
        region,
        chunk: typing.Tuple[int, int],
        data,
    ) -> dict:
        """
        will apply the fix
        :param save_file: the save-file to use
        :param dimension: the dimension in
        :param region: the region in
        :param chunk: the chunk position
        :param data: the chunk data
        :return: the transformed chunk data
        """

    @classmethod
    async def apply(cls, save_file, *args):
        for dim, region in save_file.region_iterator():
            data = await access_region_data(save_file, dim, region)
            if data is None:
                continue
            for chunk in data:
                if chunk == "version":
                    continue
                data[chunk] = await cls.fix(
                    save_file, dim, region, chunk, data["chunk"]
                )
            await write_region_data(save_file, dim, region, data)


class RegionDataFixer(IPartFixer):
    """
    Fixer for fixing an whole .region file
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    async def fix(
        cls,
        save_file,
        dimension: int,
        region,
        data,
    ) -> dict:
        """
        will apply the fix
        :param save_file: the save-file to use
        :param dimension: the dimension in
        :param region: the region in
        :param data: the region data
        :return: the transformed region data
        """

    @classmethod
    async def apply(cls, save_file, *args):
        for dim, region in save_file.region_iterator():
            data = await access_region_data(save_file, dim, region)
            if data is None:
                continue
            data = await cls.fix(save_file, dim, region, data)
            await write_region_data(save_file, dim, region, data)


class BlockRemovalFixer(IPartFixer):
    """
    Fixer for removing block-data from special blocks from the chunk system
    Will replace the block data with REPLACE (default: air-block)
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    TARGET_BLOCK_NAMES = None  # on which block(s) to apply
    REPLACE = {
        "name": "minecraft:air",
        "custom": {},
        "shown": False,
    }  # the block data to replace with

    @classmethod
    async def on_replace(
        cls,
        save_file,
        dimension: int,
        chunk: typing.Tuple[int, int],
        source,
        target,
    ):
        return target

    @classmethod
    async def apply(cls, save_file, *args):
        blocks = (
            cls.TARGET_BLOCK_NAMES
            if type(cls.TARGET_BLOCK_NAMES) in (list, tuple, set)
            else (cls.TARGET_BLOCK_NAMES,)
        )
        for dim, region in save_file.region_iterator():
            data = await access_region_data(save_file, dim, region)
            if data is None:
                continue
            for chunk in data:
                if chunk == "version":
                    continue
                palette = data[chunk]["block_palette"]
                for i, entry in enumerate(palette):
                    if entry["name"] in blocks:
                        palette[i] = await cls.on_replace(
                            save_file, dim, chunk, palette[i], cls.REPLACE
                        )
            await write_region_data(save_file, dim, region, data)


class EntityDataFixer(IPartFixer):
    """
    Fixer for fixing entity data from storage
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"
    TARGET_ENTITY_NAME = None  # which entity to apply to

    @classmethod
    async def fix(
        cls,
        save_file,
        dimension: int,
        region,
        chunk: typing.Tuple[int, int],
        data,
    ):
        """
        will apply the fix
        :param save_file: the save-file to use
        :param dimension: the dimension in
        :param region: the region in
        :param chunk: the chunk in
        :param data: the entity data
        """

    @classmethod
    async def apply(cls, save_file, *args):
        for dim, region in save_file.region_iterator():
            data = await access_region_data(save_file, dim, region)
            if data is None:
                continue
            for chunk in data:
                if chunk == "version":
                    continue
                cdata = data[chunk]
                for entity_data in cdata["entities"]:
                    if entity_data["type"] == cls.TARGET_ENTITY_NAME:
                        await cls.fix(save_file, dim, region, chunk, entity_data)
            await write_region_data(save_file, dim, region, data)


class EntityRemovalFixer(IPartFixer):
    """
    Fixer for removing an entity type from saves
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"
    TARGET_ENTITY_NAME = None  # which entity to apply to

    @classmethod
    async def on_replace(
        cls,
        save_file,
        dimension: int,
        chunk: typing.Tuple[int, int],
        previous,
        chunk_data,
    ):
        pass

    @classmethod
    async def apply(cls, save_file, *args):
        for dim, region in save_file.region_iterator():
            data = await access_region_data(save_file, dim, region)
            if data is None:
                continue
            for chunk in data:
                if chunk == "version":
                    continue
                cdata = data[chunk]
                for entity_data in cdata["entities"].copy():
                    if entity_data["type"] == cls.TARGET_ENTITY_NAME:
                        cdata["entities"].remove(entity_data)
                        await cls.on_replace(save_file, dim, chunk, entity_data, cdata)
            await write_region_data(save_file, dim, region, data)


class ChunkMapDataFixer(IPartFixer):
    """
    Fixer for changing the map data of the chunk
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    async def fix(
        cls,
        save_file,
        dimension: int,
        region,
        chunk: typing.Tuple[int, int],
        data,
    ):
        """
        Will apply the fix
        :param save_file: the save-file to use
        :param dimension: the dimension in
        :param region: the region in
        :param chunk: the chunk in
        :param data: the map data
        """

    @classmethod
    async def apply(cls, save_file, *args):
        for dim, region in save_file.region_iterator():
            data = await access_region_data(save_file, dim, region)
            if data is None:
                continue
            for chunk in data:
                if chunk == "version":
                    continue
                cdata = data[chunk]
                await cls.fix(save_file, dim, region, chunk, cdata["maps"])
            await write_region_data(save_file, dim, region, data)
