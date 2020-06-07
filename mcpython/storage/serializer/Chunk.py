"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.storage.serializer.IDataSerializer
import globals as G
import mcpython.world.Chunk
import mcpython.util.enums
import logger
import uuid


def chunk2region(cx, cz): return cx >> 5, cz >> 5


@G.registry
class Chunk(mcpython.storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    def load(cls, savefile, dimension: int, chunk: tuple, immediate=False):
        if dimension not in G.world.dimensions: return
        region = chunk2region(*chunk)
        chunk_instance: mcpython.world.Chunk.Chunk = G.world.dimensions[dimension].get_chunk(*chunk, generate=False)
        if chunk_instance.loaded: return
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: return
        if data["version"] != savefile.version:
            savefile.upgrade("minecraft:chunk", version=data["version"], dimension=dimension, region=region)
            data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))  # reload the data
        if chunk not in data: return

        G.worldgenerationhandler.enable_generation = False

        data = data[chunk]
        chunk_instance.generated = data["generated"]
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)
        for rel_position in data["blocks"]:
            position = (rel_position[0] + chunk_instance.position[0] * 16, rel_position[1],
                        rel_position[2] + chunk_instance.position[1] * 16)
            d = data["block_palette"][data["blocks"][rel_position]]

            def add(blockinstance):
                if blockinstance is None: return
                blockinstance.load(d["custom"])
                inventories = blockinstance.get_inventories()
                if "inventories" not in d: return
                for i, path in enumerate(d["inventories"]):
                    if i >= len(inventories): break
                    savefile.read("minecraft:inventory", inventory=inventories[i], path=path, file=inv_file)

            flag = d["shown"]
            if immediate:
                add(chunk_instance.add_block(position, d["name"], immediate=flag))
            else:
                # todo: add missing texture block -> insert here
                # todo: pre-check the palette and replace with air / missing_block-block (-> better performance)
                if d["name"] not in G.registry.get_by_name("block").registered_object_map:
                    logger.println("[WARN] could not add block {} at {}".format(d["name"], position))
                    continue
                G.worldgenerationhandler.task_handler.schedule_block_add(chunk_instance, position, d["name"],
                                                                         on_add=add, immediate=flag)

        positions = []
        for x in range(chunk[0]*16, chunk[0]*16+16):
            positions.extend([(x, z) for z in range(chunk[1]*16, chunk[1]*16+16)])

        try:
            chunk_instance.set_value("landmassmap", {pos: data["maps"]["landmass_palette"][data["maps"]["landmass_map"][i]]
                                                     for i, pos in enumerate(positions)})
            biome_map = {pos: data["maps"]["biome_palette"][data["maps"]["biome"][i]] for i, pos in enumerate(positions)}
            chunk_instance.set_value("biomemap", biome_map)
            chunk_instance.set_value("heightmap", {pos: data["maps"]["height"][i] for i, pos in enumerate(positions)})
        except IndexError:
            logger.write_exception("[CHUNK][CORRUPTED] palette exception in chunk '{}' in dimension '{}'".format(
                chunk, dimension))

        for entity in data["entities"]:
            if entity["type"] == "minecraft:player": continue
            try:
                entity_instance = G.entityhandler.add_entity(entity["type"], entity["position"], uuid=uuid.UUID(
                    entity["uuid"]), dimension=G.world.dimensions[dimension])
            except ValueError:
                continue
            entity_instance.rotation = entity["rotation"]
            entity_instance.harts = entity["harts"]
            entity_instance.load(entity["custom"])

        chunk_instance.loaded = True
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
        if data is None: data = {"version": savefile.version}
        if data["version"] != savefile.version:
            savefile.upgrade("minecraft:chunk", version=data["version"], dimension=dimension, region=region)
            data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
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
        G.worldgenerationhandler.enable_generation = False
        palette = cdata["block_palette"]
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)
        overridden = not override
        for position in (
                chunk_instance.positions_updated_since_last_save if not override else chunk_instance.world.keys()):
            rel_position = (position[0] - chunk_instance.position[0] * 16, position[1],
                            position[2] - chunk_instance.position[1] * 16)
            if position not in chunk_instance.world and not override:
                if rel_position in cdata["blocks"]:
                    del cdata["blocks"][rel_position]
                continue
            block = chunk_instance.world[position]
            block_data = {"custom": block.save(), "name": block.NAME, "shown": any(block.face_state.faces.values())}
            if block.get_inventories() is not None:
                block_data["inventories"] = []
                for i, inventory in enumerate(block.get_inventories()):
                    if not overridden:  # only if we need data, load it
                        savefile.dump_file_pickle(inv_file, {})
                        overridden = True
                    path = "blockinv/{}_{}_{}/{}".format(*rel_position, i)
                    savefile.dump(None, "minecraft:inventory", inventory=inventory, path=path, file=inv_file)
                    block_data["inventories"].append(path)
            if block_data in palette:
                cdata["blocks"][rel_position] = palette.index(block_data)
            else:
                cdata["blocks"][rel_position] = len(palette)
                palette.append(block_data)
        for entity in chunk_instance.entities:
            edata = {"type": entity.NAME, "position": entity.position, "rotation": entity.rotation,
                     "harts": entity.harts, "uuid": str(entity.uuid), "custom": entity.dump()}
            cdata["entities"].append(edata)
        chunk_instance.positions_updated_since_last_save.clear()

        if override:
            biome_map = chunk_instance.get_value("biomemap")

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
            cdata["maps"]["biome_palette"] = biome_palette

            height_map = chunk_instance.get_value("heightmap")
            cdata["maps"]["height"] = [height_map[pos] for pos in positions]

        data[chunk] = cdata
        savefile.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)
        G.worldgenerationhandler.enable_generation = True
