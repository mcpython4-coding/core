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

import mcpython.common.world.AbstractInterface
import mcpython.common.world.Chunk
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.IDataSerializer
import mcpython.util.enums
from mcpython import logger, shared


def chunk2region(cx, cz):
    # todo: move to util/math
    return round(cx) >> 5, round(cz) >> 5


def access_region_data(
    save_file,
    dimension: int,
    region: tuple,
):
    if dimension not in shared.world.dimensions:
        return
    return save_file.access_file_pickle(
        "dim/{}/{}_{}.region".format(dimension, *region)
    )


def write_region_data(
    save_file,
    dimension: int,
    region,
    data,
):
    save_file.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)


class BlockPartFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for fixing special block data
    Applied only ONES per block-palette entry, not ones per block. Will change all blocks of the same kind
    in that chunk
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    TARGET_BLOCK_NAME = None  # on which block(s) to apply

    @classmethod
    def fix(
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


class ChunkDataFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer targeting an whole chunk-data dict
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    def fix(
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


class RegionDataFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for fixing an whole .region file
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    def fix(
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


class BlockRemovalFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
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
    def on_replace(
        cls,
        save_file,
        dimension: int,
        chunk: typing.Tuple[int, int],
        source,
        target,
    ):
        return target


class EntityDataFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for fixing entity data from storage
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"
    TARGET_ENTITY_NAME = None  # which entity to apply to

    @classmethod
    def fix(
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


class EntityRemovalFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for removing an entity type from saves
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"
    TARGET_ENTITY_NAME = None  # which entity to apply to

    @classmethod
    def on_replace(
        cls,
        save_file,
        dimension: int,
        chunk: typing.Tuple[int, int],
        previous,
        chunk_data,
    ):
        pass


class ChunkMapDataFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for changing the map data of the chunk
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    def fix(
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
        :param data: the map data
        """


@shared.registry
class Chunk(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    def apply_part_fixer(
        cls,
        save_file,
        fixer: typing.Type[mcpython.common.world.datafixers.IDataFixer.IPartFixer],
    ):
        if issubclass(fixer, BlockPartFixer):
            blocks = (
                fixer.TARGET_BLOCK_NAME
                if type(fixer.TARGET_BLOCK_NAME) in (list, tuple, set)
                else (fixer.TARGET_BLOCK_NAME,)
            )
            for dim, region in save_file.region_iterator():
                data = access_region_data(save_file, dim, region)
                if data is None:
                    continue
                for chunk in data:
                    if chunk == "version":
                        continue
                    palette = data[chunk]["block_palette"]
                    for i, entry in enumerate(palette):
                        if entry["name"] in blocks:
                            palette[i] = fixer.fix(save_file, dim, region, chunk, entry)
                write_region_data(save_file, dim, region, data)

        elif issubclass(fixer, RegionDataFixer):
            for dim, region in save_file.region_iterator():
                data = access_region_data(save_file, dim, region)
                if data is None:
                    continue
                data = fixer.fix(save_file, dim, region, data)
                write_region_data(save_file, dim, region, data)

        elif issubclass(fixer, ChunkDataFixer):
            for dim, region in save_file.region_iterator():
                data = access_region_data(save_file, dim, region)
                if data is None:
                    continue
                for chunk in data:
                    if chunk == "version":
                        continue
                    data[chunk] = fixer.fix(
                        save_file, dim, region, chunk, data["chunk"]
                    )
                write_region_data(save_file, dim, region, data)

        elif issubclass(fixer, BlockRemovalFixer):
            blocks = (
                fixer.TARGET_BLOCK_NAMES
                if type(fixer.TARGET_BLOCK_NAMES) in (list, tuple, set)
                else (fixer.TARGET_BLOCK_NAMES,)
            )
            for dim, region in save_file.region_iterator():
                data = access_region_data(save_file, dim, region)
                if data is None:
                    continue
                for chunk in data:
                    if chunk == "version":
                        continue
                    palette = data[chunk]["block_palette"]
                    for i, entry in enumerate(palette):
                        if entry["name"] in blocks:
                            palette[i] = fixer.on_replace(
                                save_file, dim, chunk, palette[i], fixer.REPLACE
                            )
                write_region_data(save_file, dim, region, data)

        elif issubclass(fixer, EntityDataFixer):
            for dim, region in save_file.region_iterator():
                data = access_region_data(save_file, dim, region)
                if data is None:
                    continue
                for chunk in data:
                    if chunk == "version":
                        continue
                    cdata = data[chunk]
                    for entity_data in cdata["entities"]:
                        if entity_data["type"] == fixer.TARGET_ENTITY_NAME:
                            fixer.fix(save_file, dim, region, chunk, entity_data)
                write_region_data(save_file, dim, region, data)

        elif issubclass(fixer, EntityRemovalFixer):
            for dim, region in save_file.region_iterator():
                data = access_region_data(save_file, dim, region)
                if data is None:
                    continue
                for chunk in data:
                    if chunk == "version":
                        continue
                    cdata = data[chunk]
                    for entity_data in cdata["entities"].copy():
                        if entity_data["type"] == fixer.TARGET_ENTITY_NAME:
                            cdata["entities"].remove(entity_data)
                            fixer.on_replace(save_file, dim, chunk, entity_data, cdata)
                write_region_data(save_file, dim, region, data)

        elif issubclass(fixer, ChunkMapDataFixer):
            for dim, region in save_file.region_iterator():
                data = access_region_data(save_file, dim, region)
                if data is None:
                    continue
                for chunk in data:
                    if chunk == "version":
                        continue
                    cdata = data[chunk]
                    fixer.fix(save_file, dim, region, chunk, cdata["maps"])
                write_region_data(save_file, dim, region, data)

    @classmethod
    def load(
        cls, save_file, dimension: int, chunk: typing.Tuple[int, int], immediate=False
    ):
        region = chunk2region(*chunk)
        try:
            data = access_region_data(save_file, dimension, region)
        except NotImplementedError:
            return

        chunk_instance: mcpython.common.world.AbstractInterface.IChunk = (
            shared.world.dimensions[dimension].get_chunk(
                int(chunk[0]), int(chunk[1]), generate=False
            )
        )
        if chunk_instance.loaded:
            return
        if data is None:
            return
        if chunk not in data:
            return

        shared.world_generation_handler.enable_generation = False

        data = data[chunk]
        chunk_instance.generated = data["generated"]
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)
        for i, d in enumerate(data["block_palette"]):
            if d[0] not in shared.registry.get_by_name("minecraft:block").entries:
                # todo: add missing texture block -> insert here
                logger.println(
                    "[WARN] could not add block '{}' in chunk {} in dimension '{}'. Failed to look up block".format(
                        d["name"], chunk, dimension
                    )
                )
                data["block_palette"][i] = ("minecraft:air", {}, False, tuple())

        for rel_position in data["blocks"].keys():
            position = (
                rel_position[0] + chunk_instance.get_position()[0] * 16,
                rel_position[1],
                rel_position[2] + chunk_instance.get_position()[1] * 16,
            )
            d = data["block_palette"][data["blocks"][rel_position]]

            def add(instance):
                if instance is None:
                    return

                instance.inject(d[1])

                if len(d) > 3:
                    inventories = instance.get_inventories()
                    if "inventories" not in d:
                        return

                    for i, path in enumerate(d[3]):
                        if i >= len(inventories):
                            break
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

        positions = []
        for x in range(int(chunk[0] * 16), int(chunk[0] * 16 + 16)):
            positions.extend(
                [(x, z) for z in range(int(chunk[1]) * 16, int(chunk[1]) * 16 + 16)]
            )

        for data_map in chunk_instance.get_all_data_maps():
            if data_map.NAME in data["maps"]:
                data_map_data = data["maps"][data_map.NAME]
                data_map.load_from_saves(data_map_data)

        for entity in data["entities"]:
            # todo: add dynamic system for skipping
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
            entity_instance.harts = entity[3]
            if "nbt" in entity:
                entity_instance.nbt_data.update(entity[6])
            entity_instance.load(entity[5])

        chunk_instance.loaded = True
        chunk_instance.is_ready = True
        chunk_instance.visible = True
        shared.world_generation_handler.enable_generation = True

        chunk_instance.show()

    @classmethod
    def save(cls, data, save_file, dimension: int, chunk: tuple, override=False):
        if dimension not in shared.world.dimensions:
            return

        if chunk not in shared.world.dimensions[dimension].chunks:
            return

        region = chunk2region(*chunk)
        chunk_instance: mcpython.common.world.AbstractInterface.IChunk = (
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
        palette = cdata[
            "block_palette"
        ]  # list of {"custom": <some stuff>, "name": <name>, "shown": <shown>, ...}

        inv_file = "dim/{}/{}_{}.inv".format(
            dimension, *region
        )  # where to dump inventory stuff
        overridden = not override
        for position in (
            chunk_instance.get_positions_updated_since_last_save()
            if not override
            else (e[0] for e in chunk_instance)
        ):
            rel_position = (
                position[0] - chunk_instance.get_position()[0] * 16,
                position[1],
                position[2] - chunk_instance.get_position()[1] * 16,
            )  # the relative position to the chunk

            block = chunk_instance.get_block(position, none_if_str=True)

            assert not isinstance(block, str), "something is really wrong!"

            if block is None and not override:
                if rel_position in cdata["blocks"]:
                    del cdata["blocks"][rel_position]  # ok, old data MUST be removed
                continue

            block_data = (
                block.NAME,
                block.dump_data(),
                any(block.face_state.faces.values()),
            )

            # inventory data
            # todo: move to custom function in Block-class
            if block.get_inventories() is not None:  # have we any inventory of stuff
                block_data = block_data + ([],)

                # iterate over all inventories
                for i, inventory in enumerate(block.get_inventories()):
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
                entity.harts,
                str(entity.uuid),
                entity.dump(),
                entity.nbt_data,
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
