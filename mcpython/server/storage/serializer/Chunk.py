"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.server.storage.serializer.IDataSerializer
import mcpython.server.storage.datafixers.IDataFixer
from mcpython import globals as G, logger
import mcpython.common.world.Chunk
import mcpython.util.enums
import uuid


def chunk2region(cx, cz): return cx >> 5, cz >> 5


def access_region_data(savefile, dimension: int, region: tuple):
    if dimension not in G.world.dimensions: return
    return savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))


def write_region_data(savefile, dimension, region, data):
    savefile.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)


class BlockPartFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for fixing special block data
    Applied only ONES per block-palette entry, not ones per block. Will change all blocks of the same kind
    in that chunk
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    TARGET_BLOCK_NAME = None  # on which block(s) to apply

    @classmethod
    def fix(cls, savefile, dim, region, chunk, data) -> dict:
        """
        called to apply the fix
        :param savefile: the savefile-instance to use
        :param dim: the dim in
        :param region: the region in
        :param chunk: the chunk in
        :param data: the block data
        :return: the transformed data
        """


class ChunkDataFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    fixer targeting an whole chunk-data dict
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    def fix(cls, savefile, dim, region, chunk, data) -> dict:
        """
        will apply the fix
        :param savefile: the savefile to use
        :param dim: the dimension in
        :param region: the region in
        :param chunk: the chunk position
        :param data: the chunk data
        :return: the transformed chunk data
        """


class RegionDataFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    fixer for fixing an whole .region file
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    def fix(cls, savefile, dim, region, data) -> dict:
        """
        will apply the fix
        :param savefile: the savefile to use
        :param dim: the dimension in
        :param region: the region in
        :param data: the region data
        :return: the transformed region data
        """


class BlockRemovalFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for removing block-data from special blocks from the chunk system
    Will replace the block data with REPLACE (default: air-block)
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    TARGET_BLOCK_NAMES = None  # on which block(s) to apply
    REPLACE = {"name": "minecraft:air", "custom": {}, "shown": False}  # the block data to replace with


class EntityDataFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for fixing entity data from storage
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"
    TARGET_ENTITY_NAME = None  # which entity to apply to

    @classmethod
    def fix(cls, savefile, dim, region, chunk, data):
        """
        will apply the fix
        :param savefile: the savefile to use
        :param dim: the dimension in
        :param region: the region in
        :param chunk: the chunk in
        :param data: the entity data
        """


class EntityRemovalFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for removing an entity type from saves
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"
    TARGET_ENTITY_NAME = None  # which entity to apply to


class ChunkMapDataFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    Fixer for changing the map data of the chunk
    """

    TARGET_SERIALIZER_NAME = "minecraft:chunk"

    @classmethod
    def fix(cls, savefile, dim, region, chunk, data):
        """
        will apply the fix
        :param savefile: the savefile to use
        :param dim: the dimension in
        :param region: the region in
        :param chunk: the chunk in
        :param data: the map data
        """


@G.registry
class Chunk(mcpython.server.storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    def apply_part_fixer(cls, savefile, fixer):
        if issubclass(fixer, BlockPartFixer):
            blocks = (fixer.TARGET_BLOCK_NAME if type(fixer.TARGET_BLOCK_NAME) in (list, tuple, set) else
                      (fixer.TARGET_BLOCK_NAME,))
            for dim, region in savefile.region_iterator():
                data = access_region_data(savefile, dim, region)
                if data is None: continue
                for chunk in data:
                    if chunk == "version": continue
                    palette = data[chunk]["block_palette"]
                    for i, entry in enumerate(palette):
                        if entry["name"] in blocks:
                            palette[i] = fixer.fix(savefile, dim, region, chunk, entry)
                write_region_data(savefile, dim, region, data)

        elif issubclass(fixer, RegionDataFixer):
            for dim, region in savefile.region_iterator():
                data = access_region_data(savefile, dim, region)
                if data is None: continue
                data = fixer.fix(savefile, dim, region, data)
                write_region_data(savefile, dim, region, data)

        elif issubclass(fixer, ChunkDataFixer):
            for dim, region in savefile.region_iterator():
                data = access_region_data(savefile, dim, region)
                if data is None: continue
                for chunk in data:
                    if chunk == "version": continue
                    data[chunk] = fixer.fix(savefile, dim, region, chunk, data["chunk"])
                write_region_data(savefile, dim, region, data)

        elif issubclass(fixer, BlockRemovalFixer):
            blocks = (fixer.TARGET_BLOCK_NAMES if type(fixer.TARGET_BLOCK_NAMES) in (list, tuple, set) else
                      (fixer.TARGET_BLOCK_NAMES,))
            for dim, region in savefile.region_iterator():
                data = access_region_data(savefile, dim, region)
                if data is None: continue
                for chunk in data:
                    if chunk == "version": continue
                    palette = data[chunk]["block_palette"]
                    for i, entry in enumerate(palette):
                        if entry["name"] in blocks:
                            palette[i] = fixer.REPLACE
                write_region_data(savefile, dim, region, data)

        elif issubclass(fixer, EntityDataFixer):
            for dim, region in savefile.region_iterator():
                data = access_region_data(savefile, dim, region)
                if data is None: continue
                for chunk in data:
                    if chunk == "version": continue
                    cdata = data[chunk]
                    for entity_data in cdata["entities"]:
                        if entity_data["type"] == fixer.TARGET_ENTITY_NAME:
                            fixer.fix(savefile, dim, region, chunk, entity_data)
                write_region_data(savefile, dim, region, data)

        elif issubclass(fixer, EntityRemovalFixer):
            for dim, region in savefile.region_iterator():
                data = access_region_data(savefile, dim, region)
                if data is None: continue
                for chunk in data:
                    if chunk == "version": continue
                    cdata = data[chunk]
                    for entity_data in cdata["entities"].copy():
                        if entity_data["type"] == fixer.TARGET_ENTITY_NAME:
                            cdata["entities"].remove(entity_data)
                write_region_data(savefile, dim, region, data)

        elif issubclass(fixer, ChunkMapDataFixer):
            for dim, region in savefile.region_iterator():
                data = access_region_data(savefile, dim, region)
                if data is None: continue
                for chunk in data:
                    if chunk == "version": continue
                    cdata = data[chunk]
                    fixer.fix(savefile, dim, region, chunk, cdata["maps"])
                write_region_data(savefile, dim, region, data)

    @classmethod
    def load(cls, savefile, dimension: int, chunk: tuple, immediate=False):
        region = chunk2region(*chunk)
        try:
            data = access_region_data(savefile, dimension, region)
        except NotImplementedError:
            return

        chunk_instance: mcpython.world.Chunk.Chunk = G.world.dimensions[dimension].get_chunk(*chunk, generate=False)
        if chunk_instance.loaded: return
        if data is None: return
        if chunk not in data: return

        G.worldgenerationhandler.enable_generation = False

        data = data[chunk]
        chunk_instance.generated = data["generated"]
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)
        for i, d in enumerate(data["block_palette"]):
            if d["name"] not in G.registry.get_by_name("block").registered_object_map:
                # todo: add missing texture block -> insert here
                logger.println("[WARN] could not add block '{}' in chunk {} in dimension '{}'. Failed to look up block".
                               format(d["name"], chunk, dimension))
                data["block_palette"][i] = {"shown": False, "name": "minecraft:air", "custom": {}}
                continue
        for rel_position in data["blocks"].keys():
            position = (rel_position[0] + chunk_instance.position[0] * 16, rel_position[1],
                        rel_position[2] + chunk_instance.position[1] * 16)
            d = data["block_palette"][data["blocks"][rel_position]]

            def add(blockinstance):
                if blockinstance is None: return
                blockinstance.inject(d["custom"])
                inventories = blockinstance.get_inventories()
                if "inventories" not in d: return
                for i, path in enumerate(d["inventories"]):
                    if i >= len(inventories): break
                    savefile.read("minecraft:inventory", inventory=inventories[i], path=path, file=inv_file)

            flag = d["shown"]
            if immediate:
                add(chunk_instance.add_block(position, d["name"], immediate=flag))
            else:
                G.worldgenerationhandler.task_handler.schedule_block_add(chunk_instance, position, d["name"],
                                                                         on_add=add, immediate=flag)

        positions = []
        for x in range(chunk[0] * 16, chunk[0] * 16 + 16):
            positions.extend([(x, z) for z in range(chunk[1] * 16, chunk[1] * 16 + 16)])

        if "landmass_map" in data["maps"] and "biome" in data["maps"] and "height" in data["maps"] and \
                sum([len(data["maps"][key]) for key in data["maps"]]) == len(data["maps"]) * 256:
            try:
                chunk_instance.set_value("landmassmap",
                                         {pos: data["maps"]["landmass_palette"][data["maps"]["landmass_map"][i]]
                                          for i, pos in enumerate(positions)})
                biome_map = {pos: data["maps"]["biome_palette"][data["maps"]["biome"][i]] for i, pos in
                             enumerate(positions)}
                chunk_instance.set_value("biomemap", biome_map)
                chunk_instance.set_value("heightmap",
                                         {pos: data["maps"]["height"][i] for i, pos in enumerate(positions)})
            except IndexError:
                logger.print_exception(
                    "[CHUNK][CORRUPTED] palette map exception in chunk '{}' in dimension '{}'".format(
                        chunk, dimension),
                    "this might indicate an unsuccessful save of the world!")

        for entity in data["entities"]:
            if entity["type"] == "minecraft:player": continue
            try:
                entity_instance = G.entityhandler.add_entity(entity["type"], entity["position"], uuid=uuid.UUID(
                    entity["uuid"]), dimension=G.world.dimensions[dimension])
            except ValueError:
                continue
            except:
                logger.print_exception("error during loading entity data {} in chunk {} in dimension '{}'".format(
                    entity, chunk, dimension))
                continue
            entity_instance.rotation = entity["rotation"]
            entity_instance.harts = entity["harts"]
            if "nbt" in entity:
                entity_instance.nbt_data.update(entity["nbt"])
            entity_instance.load(entity["custom"])

        chunk_instance.loaded = True
        chunk_instance.is_ready = True
        chunk_instance.visible = True
        G.worldgenerationhandler.enable_generation = True

        chunk_instance.show()

    @classmethod
    def save(cls, data, savefile, dimension: int, chunk: tuple, override=False):
        if dimension not in G.world.dimensions: return
        if chunk not in G.world.dimensions[dimension].chunks: return
        region = chunk2region(*chunk)
        chunk_instance: mcpython.world.Chunk.Chunk = G.world.dimensions[dimension].chunks[chunk]
        if not chunk_instance.generated: return
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: data = {}
        if chunk in data and not override:
            cdata = data[chunk]
            override = False
        else:
            cdata = {
                "dimension": dimension,
                "position": chunk,
                "blocks": {},
                "block_palette": [],
                "generated": chunk_instance.generated,
                "maps": {
                    "landmass_map": [None] * 16 ** 2,
                    "landmass_palette": [],
                    # "temperature": [None] * 16 ** 2,
                    "biome": [0] * 16 ** 2,
                    "biome_palette": [],
                    "height": [None] * 16 ** 2
                },
                "entities": []
            }
            override = True

        # when doing stuff, please make sure that nothing fancy happens
        G.worldgenerationhandler.enable_generation = False

        # these section is for dumping block stuff...
        palette = cdata["block_palette"]  # list of {"custom": <some stuff>, "name": <name>, "shown": <shown>, ...}

        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)  # where to dump inventory stuff
        overridden = not override
        for position in (
                chunk_instance.positions_updated_since_last_save if not override else chunk_instance.world.keys()):
            rel_position = (position[0] - chunk_instance.position[0] * 16, position[1],
                            position[2] - chunk_instance.position[1] * 16)  # the relative position to the chunk
            if position not in chunk_instance.world and not override:
                if rel_position in cdata["blocks"]:
                    del cdata["blocks"][rel_position]  # ok, old data MUST be removed
                continue
            block = chunk_instance.world[position]
            block_data = {"custom": block.dump(), "name": block.NAME, "shown": any(block.face_state.faces.values())}

            # inventory data
            # todo: move to custom function in Block-class
            if block.get_inventories() is not None:  # have we any inventory of stuff
                block_data["inventories"] = []  # create the entry for the data
                for i, inventory in enumerate(block.get_inventories()):  # iterate over all inventories
                    if not overridden:  # only if we need data, load it
                        savefile.dump_file_pickle(inv_file, {})
                        overridden = True
                    path = "blockinv/{}_{}_{}/{}".format(*rel_position, i)  # were to locate in the file
                    savefile.dump(None, "minecraft:inventory", inventory=inventory, path=path, file=inv_file)
                    block_data["inventories"].append(path)

            # dump into the palette table
            if block_data in palette:
                cdata["blocks"][rel_position] = palette.index(block_data)
            else:
                cdata["blocks"][rel_position] = len(palette)
                palette.append(block_data)
        chunk_instance.positions_updated_since_last_save.clear()

        # this is about entity stuff...
        # todo: move completely to Entity-API
        for entity in chunk_instance.entities:
            edata = {"type": entity.NAME, "position": entity.position, "rotation": entity.rotation,
                     "harts": entity.harts, "uuid": str(entity.uuid), "custom": entity.dump(), "nbt": entity.nbt_data}
            cdata["entities"].append(edata)

        if override:  # we want to re-dump all data maps
            biome_map = chunk_instance.get_value("biomemap")  # read the biome map ...

            # ... and use it as an template for the following
            # todo: use something else more stable!
            positions = list(biome_map.keys())  # an list of all (x, z) in the chunk, for sorting the arrays
            positions.sort(key=lambda x: x[1])
            positions.sort(key=lambda x: x[0])

            landmass_map = chunk_instance.get_value("landmassmap")
            cdata["maps"]["landmass_map"] = []
            cdata["maps"]["landmass_palette"] = []
            for pos in positions:
                mass = landmass_map[pos]
                if mass not in cdata["maps"]["landmass_palette"]:
                    index = len(cdata["maps"]["landmass_palette"])
                    cdata["maps"]["landmass_palette"].append(mass)
                else:
                    index = cdata["maps"]["landmass_palette"].index(mass)
                cdata["maps"]["landmass_map"].append(index)

            # temperature_map = chunk_instance.get_value("temperaturemap")
            # cdata["maps"]["temperature"] = [temperature_map[pos] for pos in positions]

            biome_palette = []
            biomes = []
            for pos in positions:
                if biome_map[pos] not in biome_palette:
                    index = len(biome_palette)
                    biome_palette.append(biome_map[pos])
                else:
                    index = biome_palette.index(biome_map[pos])
                biomes.append(index)
            cdata["maps"]["biome"] = biomes
            cdata["maps"]["biome_palette"] = biome_palette  # todo: move to global map of biomes

            height_map = chunk_instance.get_value("heightmap")
            cdata["maps"]["height"] = [height_map[pos] for pos in positions]

        data[chunk] = cdata  # dump the chunk into the region
        write_region_data(savefile, dimension, region, data)  # and dump the region to the file

        G.worldgenerationhandler.enable_generation = True  # re-enable world gen as we are finished
        # todo: make sure that this is always set back to True, also on error
