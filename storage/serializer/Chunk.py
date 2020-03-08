import storage.serializer.IDataSerializer
import globals as G
import world.Chunk
import util.enums


def chunk2region(cx, cz): return cx >> 5, cz >> 5


@G.registry
class Chunk(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    def load(cls, savefile, dimension: int, chunk: tuple, immediate=True):
        if dimension not in G.world.dimensions: return
        region = chunk2region(*chunk)
        chunk_instance: world.Chunk.Chunk = G.world.dimensions[dimension].get_chunk(*chunk, generate=False)
        if chunk_instance.loaded: return
        chunk_instance.loaded = True
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: return
        if data["version"] != savefile.version:
            savefile.upgrade("minecraft:chunk", version=data["version"], dimension=dimension, chunk=chunk)
            data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))  # reload the data
        if chunk not in data: return
        data = data[chunk]
        chunk_instance.generated = data["generated"]
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)
        for position in data["blocks"]:
            d = data["block_palette"][data["blocks"][position]]

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
                if d["name"] not in G.registry.get_by_name("block").registered_object_map: continue
                chunk_instance.add_add_block_gen_task(position, d["name"], on_add=add, immediate=flag)

        positions = []
        for x in range(chunk[0]*16, chunk[0]*16+16):
            positions.extend([(x, z) for z in range(chunk[1]*16, chunk[1]*16+16)])

        chunk_instance.set_value("landmassmap", data["maps"]["landmass"])
        chunk_instance.set_value("temperaturemap", data["maps"]["temperature"])
        biome_map = {pos: data["maps"]["biome_palette"][data["maps"]["biome"][i]] for i, pos in enumerate(positions)}
        chunk_instance.set_value("biomemap", biome_map)
        chunk_instance.set_value("heightmap", data["maps"]["height"])

    @classmethod
    def save(cls, data, savefile, dimension: int, chunk: tuple):
        if dimension not in G.world.dimensions: return
        if chunk not in G.world.dimensions[dimension].chunks: return
        region = chunk2region(*chunk)
        chunk_instance: world.Chunk.Chunk = G.world.dimensions[dimension].chunks[chunk]
        palette = []
        blocks = {}
        inv_file = "dim/{}/{}_{}.inv".format(dimension, *region)
        overridden = False
        for position in chunk_instance.world:
            block = chunk_instance.world[position]
            block_data = {"custom": block.save(), "name": block.NAME, "shown": any(block.face_state.faces.values())}
            if block.get_inventories() is not None:
                block_data["inventories"] = []
                for i, inventory in enumerate(block.get_inventories()):
                    if not overridden:  # only if we need data, load it
                        savefile.dump_file_pickle(inv_file, {})
                        overridden = True
                    path = "blockinv/{}_{}_{}/{}".format(*position, i)
                    savefile.dump(None, "minecraft:inventory", inventory=inventory, path=path, file=inv_file)
                    block_data["inventories"].append(path)
            if block_data in palette:
                blocks[position] = palette.index(block_data)
            else:
                blocks[position] = len(palette)
                palette.append(block_data)
        landmass_map = chunk_instance.get_value("landmassmap")
        temperature_map = chunk_instance.get_value("temperaturemap")
        biome_map = chunk_instance.get_value("biomemap")

        positions = list(biome_map.keys())  # an list of all (x, z) in the chunk, for sorting the arrays
        positions.sort(key=lambda x: x[1])
        positions.sort(key=lambda x: x[0])

        biome_palette = []
        biomes = []
        for pos in positions:
            if biome_map[pos] not in biome_palette:
                index = len(biome_palette)
                biome_palette.append(biome_map[pos])
            else:
                index = biome_palette.index(biome_map[pos])
            biomes.append(index)
        height_map = chunk_instance.get_value("heightmap")
        cdata = {
            "dimension": dimension,
            "position": chunk,
            "blocks": blocks,
            "block_palette": palette,
            "generated": chunk_instance.generated,
            "maps": {
                "landmass": landmass_map,
                "temperature": temperature_map,
                "biome": biomes,
                "biome_palette": biome_palette,
                "height": height_map
            }
        }
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: data = {"version": savefile.version}
        if data["version"] != savefile.version:
            savefile.upgrade("chunk", data["version"], dimension=dimension, chunk=chunk)
            data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        data[chunk] = cdata
        savefile.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)

