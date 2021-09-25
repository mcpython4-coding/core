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
import uuid

import mcpython.engine.world.AbstractInterface
import mcpython.common.world.Chunk
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.IDataSerializer
import mcpython.util.enums
from mcpython import shared
from mcpython.common.world.serializer.util import (
    access_region_data,
    chunk2region,
    write_region_data,
)
from mcpython.engine import logger


@shared.registry
class Chunk(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    def load(
        cls, save_file, dimension: int, chunk: typing.Tuple[int, int], immediate=False
    ):
        region = chunk2region(*chunk)
        try:
            data = access_region_data(save_file, dimension, region)
        except NotImplementedError:
            return

        chunk_instance: mcpython.engine.world.AbstractInterface.IChunk = (
            shared.world.dimensions[dimension].get_chunk(
                int(chunk[0]), int(chunk[1]), generate=False
            )
        )

        # So, in some cases we cannot load the chunk
        if chunk_instance.loaded:
            return
        if data is None:
            return
        if chunk not in data:
            return

        # Don't do this when we are saving stuff
        shared.world_generation_handler.enable_generation = False

        data = data[chunk]
        chunk_instance.generated = data["generated"]

        # This file stores the inventory data
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)

        # Prepare the block palette for later usage
        for i, d in enumerate(data["block_palette"]):
            if d[0] not in shared.registry.get_by_name("minecraft:block").entries:
                # todo: add missing texture block -> insert here
                logger.println(
                    "[WARN] could not add block '{}' in chunk {} in dimension '{}'. Failed to look up block".format(
                        d[0], chunk, dimension
                    )
                )
                data["block_palette"][i] = ("minecraft:air", {}, False, tuple())

        # So, this are all blocks in the map...
        # todo: make sector based and DON'T use a dict! (Ints can be stored a lot better than this map)
        for rel_position in data["blocks"].keys():
            position = (
                rel_position[0] + chunk_instance.get_position()[0] * 16,
                rel_position[1],
                rel_position[2] + chunk_instance.get_position()[1] * 16,
            )
            d = data["block_palette"][data["blocks"][rel_position]]

            cls.add_block_to_world(
                chunk_instance, d, immediate, position, save_file, inv_file
            )

        for data_map in chunk_instance.get_all_data_maps():
            if data_map.NAME in data["maps"]:
                data_map_data = data["maps"][data_map.NAME]
                data_map.load_from_saves(data_map_data)

        for entity in data["entities"]:
            # todo: add dynamic system for skipping by attribute
            if entity[0] == "minecraft:player":
                continue

            try:
                entity_instance = shared.entity_manager.spawn_entity(
                    entity[0],
                    entity[1],
                    uuid=uuid.UUID(entity[4]),
                    dimension=shared.world.dimensions[dimension],
                )
            except ValueError:
                continue
            except:
                logger.print_exception(
                    "error during loading entity data {} in chunk {} in dimension '{}'".format(
                        entity, chunk, dimension
                    )
                )
                continue

            entity_instance.rotation = entity[2]
            entity_instance.hearts = entity[3]
            if "nbt" in entity:
                entity_instance.nbt_data.update(entity[6])
            entity_instance.load(entity[5])

            if len(entity) == 8:
                entity_instance.deserialize_container(entity[7])

        chunk_instance.loaded = True
        chunk_instance.is_ready = True
        chunk_instance.visible = True
        shared.world_generation_handler.enable_generation = True

        chunk_instance.show()

    @classmethod
    def add_block_to_world(
        cls, chunk_instance, d, immediate, position, save_file, inv_file
    ):
        # helper for setting up the block
        def add(instance):
            if instance is None:
                return

            instance.inject(d[1])

            if len(d) > 3:
                inventories = instance.get_inventories()
                for i, path in enumerate(d[3]):
                    if i >= len(inventories):
                        break

                    if inventories[i] is None:
                        continue

                    save_file.read(
                        "minecraft:inventory",
                        inventory=inventories[i],
                        path=path,
                        file=inv_file,
                    )

        flag = d[2]
        if immediate:
            add(chunk_instance.add_block(position, d[0], immediate=flag))
        else:
            shared.world_generation_handler.task_handler.schedule_block_add(
                chunk_instance, position, d[0], on_add=add, immediate=flag
            )

    @classmethod
    def save(cls, data, save_file, dimension: int, chunk: tuple, override=False):
        if dimension not in shared.world.dimensions:
            return

        if chunk not in shared.world.dimensions[dimension].chunks:
            return

        region = chunk2region(*chunk)
        chunk_instance: mcpython.engine.world.AbstractInterface.IChunk = (
            shared.world.dimensions[dimension].chunks[chunk]
        )

        data = save_file.access_file_pickle(
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
                "entities": [],
                "maps": {},
            }
            # And mark that all data should be written
            override = True

        # When doing stuff, please make sure that nothing fancy happens with chunks
        shared.world_generation_handler.enable_generation = False

        # Load the block palette
        # list of {"custom": <some stuff>, "name": <name>, "shown": <shown>, ...}
        palette = cdata["block_palette"]

        # where to dump inventory stuff
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)
        overridden = not override

        for position in (
            chunk_instance.get_positions_updated_since_last_save()
            if not override
            else (e[0] for e in chunk_instance)
        ):
            # the relative position to the chunk
            rel_position = (
                position[0] - chunk_instance.get_position()[0] * 16,
                position[1],
                position[2] - chunk_instance.get_position()[1] * 16,
            )

            block = chunk_instance.get_block(position, none_if_str=True)

            if block is None and not override:
                if rel_position in cdata["blocks"]:
                    del cdata["blocks"][rel_position]  # ok, old data MUST be removed

                continue

            if isinstance(block, str):
                if rel_position in cdata["blocks"]:
                    del cdata["blocks"][
                        rel_position
                    ]  # ok, invalid data MUST be removed

                continue

            block_data = (
                block.NAME,
                block.dump_data(),
                any(block.face_info.faces.values()),
            )

            # inventory data
            # todo: move to custom function in Block-class
            if block.get_inventories() is not None:  # have we any inventory of stuff
                block_data = block_data + ([],)

                # iterate over all inventories
                for i, inventory in enumerate(block.get_inventories()):
                    if inventory is None:
                        block_data[3].append(None)
                        continue

                    # only if we need data, load it
                    if not overridden:
                        save_file.dump_file_pickle(inv_file, {})
                        overridden = True

                    # were to locate in the file
                    path = "blockinv/{}_{}_{}/{}".format(*rel_position, i)

                    save_file.dump(
                        None,
                        "minecraft:inventory",
                        inventory=inventory,
                        path=path,
                        file=inv_file,
                    )
                    block_data[3].append(path)

            # Dump into the palette table
            if block_data in palette:
                cdata["blocks"][rel_position] = palette.index(block_data)
            else:
                cdata["blocks"][rel_position] = len(palette)
                palette.append(block_data)

        chunk_instance.clear_positions_updated_since_last_save()

        # this is about entity stuff...
        # todo: move completely to Entity-API
        for entity in chunk_instance.get_entities():
            entity_data = (
                entity.NAME,
                entity.position,
                entity.rotation,
                entity.hearts,
                str(entity.uuid),
                entity.dump(),
                entity.nbt_data,
                entity.serialize_container(),
            )
            cdata["entities"].append(entity_data)

        if override:  # we want to re-dump all data maps
            for data_map in chunk_instance.get_all_data_maps():
                cdata["maps"][data_map.NAME] = data_map.dump_for_saves()

        data[chunk] = cdata  # dump the chunk into the region
        write_region_data(
            save_file, dimension, region, data
        )  # and dump the region to the file

        shared.world_generation_handler.enable_generation = (
            True  # re-enable world gen as we are finished
        )
        # todo: make sure that this is always set back to True, also on error
