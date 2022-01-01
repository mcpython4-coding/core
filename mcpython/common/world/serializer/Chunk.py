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
import itertools
import typing
import uuid

import mcpython.common.world.Chunk
from mcpython.engine.world.AbstractInterface import IChunk
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.IDataSerializer as IDataSerializer
import mcpython.engine.world.AbstractInterface
import mcpython.util.enums
from mcpython import shared
from mcpython.common.world.serializer.util import (
    access_region_data,
    chunk2region,
    write_region_data,
)
from mcpython.engine import logger
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


@shared.registry
class Chunk(IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    async def load(
        cls, save_file, dimension: int, chunk: typing.Tuple[int, int], immediate=False
    ):
        region = chunk2region(*chunk)
        try:
            data = await access_region_data(save_file, dimension, region)
        except NotImplementedError:
            return

        dcx, dcz = (e * 16 for e in chunk)

        chunk_instance: mcpython.engine.world.AbstractInterface.IChunk = (
            shared.world.dimensions[dimension].get_chunk(
                int(chunk[0]), int(chunk[1]), generate=False
            )
        )

        # So, in some cases we should not load the chunk
        if chunk_instance.loaded:
            return
        if data is None:
            return
        if chunk not in data:
            return

        # Don't generate stuff while we are saving stuff
        shared.world_generation_handler.enable_generation = False

        data = data[chunk]
        chunk_instance.generated = data["generated"]

        # todo: remove stuff which is not in the registries!

        buffer = ReadBuffer(data["blocks"])
        height = buffer.read_uint()
        for x, y, z in itertools.product(range(16), range(height), range(16)):
            index = buffer.read_uint()
            position = (x+dcx, y, z+dcz)

            if index == 0:
                await chunk_instance.remove_block(position)
            else:
                block_buffer = ReadBuffer(data["block_palette"][index-1])
                name = block_buffer.read_string()
                visible = block_buffer.read_bool()

                await cls.add_block_to_world(
                    chunk_instance, block_buffer, immediate, position, name, visible
                )

        entity_buffer = ReadBuffer(data["entities"])

        async def read_entity():
            type_name = entity_buffer.read_string()
            if type_name == "minecraft:player": return

            await shared.entity_manager.registry[type_name].create_from_buffer(entity_buffer)
            # todo: do we need to do anything else?

        await entity_buffer.collect_list(read_entity)

        map_buffer = ReadBuffer(data["maps"])
        current_type_name = None

        async def read_map_key():
            nonlocal current_type_name
            current_type_name = map_buffer.read_string()

        async def read_map_value():
            if current_type_name not in chunk_instance.data_maps:
                logger.println(f"[DATA MAP][WARN] skipping deserialization of map {current_type_name}")
                return

            await chunk_instance.data_maps[current_type_name].read_from_network_buffer(map_buffer)

        await map_buffer.read_dict(read_map_key, read_map_value)

        chunk_instance.loaded = True
        chunk_instance.is_ready = True
        chunk_instance.visible = True
        shared.world_generation_handler.enable_generation = True

        chunk_instance.show()

    @classmethod
    async def add_block_to_world(
        cls, chunk_instance, block_buffer: ReadBuffer, immediate, position, name, visible
    ):
        # helper for setting up the block
        async def add(instance):
            if instance is None:
                return

            await instance.read_from_network_buffer(block_buffer)

        if immediate:
            await add(chunk_instance.add_block(position, name, immediate=visible))
        else:
            shared.world_generation_handler.task_handler.schedule_block_add(
                chunk_instance, position, name, on_add=add, immediate=visible
            )

    @classmethod
    async def save(cls, data, save_file, dimension: int, chunk: tuple, override=False):
        if dimension not in shared.world.dimensions or chunk not in shared.world.dimensions[dimension].chunks:
            return

        region = chunk2region(*chunk)
        dcx, dcz = (e * 16 for e in chunk)
        chunk_instance: IChunk = shared.world.get_dimension(dimension).get_chunk(chunk)

        # region = await save_file.get_region_access(dimension, region)
        # target_buffer = WriteBuffer()

        data = await save_file.access_file_pickle_async(
            "dim/{}/{}_{}.region".format(dimension, *region)
        )

        # If the file does not exist, create a empty region
        if data is None:
            data = {}

        # If the chunk exists, the chunk data is arrival
        if chunk in data and not override:
            cdata = data[chunk]

        # Otherwise, we need to create a dummy object for later filling
        else:
            cdata = {
                "dimension": dimension,
                "position": chunk,
                "blocks": {},
                "block_palette": [],
                "generated": chunk_instance.is_generated(),
                "entities": bytes(),
                "maps": bytes(),
            }
            # And mark that all data should be written
            override = True

        # When doing stuff, please make sure that nothing fancy happens with chunks
        shared.world_generation_handler.enable_generation = False

        # Load the block palette
        # list of {"custom": <some stuff>, "name": <name>, "shown": <shown>, ...}

        block_buffer = WriteBuffer()
        palette = []

        block_buffer.write_uint(256)
        for x, y, z in itertools.product(range(16), range(256), range(16)):
            block = chunk_instance.get_block((x+dcx, y, z+dcz), none_if_str=True)

            if block is None:
                block_buffer.write_uint(0)
            else:
                block_instance_buffer = WriteBuffer()
                block_instance_buffer.write_string(block.NAME)
                block_instance_buffer.write_bool(bool(block.face_info.faces) if block.face_info is not None else False)
                await block.write_to_network_buffer(block_instance_buffer)

                block_data = block_instance_buffer.get_data()
                if block_data in palette:
                    block_buffer.write_uint(palette.index(block_data)+1)
                else:
                    palette.append(block_data)
                    block_buffer.write_uint(len(palette))

        cdata["block_palette"] = palette
        # target_buffer.write_list(palette, lambda e: target_buffer.write_const_bytes(e))

        cdata["blocks"] = block_buffer.get_data()
        # target_buffer.write_sub_buffer(block_buffer)

        chunk_instance.clear_positions_updated_since_last_save()

        entity_buffer = WriteBuffer()

        async def write_entity(entity):
            entity_buffer.write_string(entity.NAME)
            await entity.write_to_network_buffer(entity_buffer)

        await entity_buffer.write_list(chunk_instance.get_entities(), write_entity)
        cdata["entities"] = entity_buffer.get_data()

        if override:  # we want to re-dump all data maps
            map_buffer = WriteBuffer()

            async def write_map(data_map):
                await data_map.write_to_network_buffer(map_buffer)

            async def write_key(name):
                map_buffer.write_string(name)

            await map_buffer.write_dict(chunk_instance.data_maps, write_key, write_map)
            cdata["maps"] = map_buffer.get_data()
            # target_buffer.write_sub_buffer(map_buffer)
        else:
            pass
            # todo: remove if-else check and write anyway

        # dump the chunk into the region
        data[chunk] = cdata

        # and dump the region to the file
        await write_region_data(save_file, dimension, region, data)

        # region.write_chunk_data(*chunk, target_buffer)

        # re-enable world gen as we are finished
        shared.world_generation_handler.enable_generation = True

        # todo: make sure that this is always set back to True, also on error
