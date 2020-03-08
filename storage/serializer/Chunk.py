import storage.serializer.IDataSerializer
import globals as G
import world.Chunk
import util.enums


@G.registry
class Chunk(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    def load(cls, savefile, dimension: int, chunk: tuple, immediate=True):
        if dimension not in G.world.dimensions: return
        chunk_instance: world.Chunk.Chunk = G.world.dimensions[dimension].get_chunk(*chunk, generate=False)
        if chunk_instance.loaded: return
        chunk_instance.loaded = True
        data = savefile.access_file_pickle("dim/{}/{}_{}.chunk".format(dimension, *chunk))
        if data is None: return
        if data["version"] != savefile.version:
            savefile.upgrade("minecraft:chunk", version=data["version"], dimension=dimension, chunk=chunk)
            data = savefile.access_file_pickle("dim/{}/{}_{}.chunk".format(dimension, *chunk)) # reload the data
        chunk_instance.generated = data["generated"]
        for position in data["blocks"]:
            d = data["block_palette"][data["blocks"][position]]

            def add(blockinstance):
                if blockinstance is None: return
                blockinstance.load(d["custom"])
                inventories = blockinstance.get_inventories()
                if "inventories" not in d: return
                for i, path in enumerate(d["inventories"]):
                    if i >= len(inventories): break
                    savefile.read("minecraft:inventory", inventory=inventories[i], path=path)

            flag = d["shown"]
            if immediate:
                add(chunk_instance.add_block(position, d["name"], immediate=flag))
            else:
                if d["name"] not in G.registry.get_by_name("block").registered_object_map: continue
                chunk_instance.add_add_block_gen_task(position, d["name"], on_add=add, immediate=flag)
        chunk_instance.set_value("landmassmap", data["maps"]["landmass"])
        chunk_instance.set_value("temperaturemap", data["maps"]["temperature"])
        chunk_instance.set_value("biomemap", data["maps"]["biome"])
        chunk_instance.set_value("heightmap", data["maps"]["height"])

    @classmethod
    def save(cls, data, savefile, dimension: int, chunk: tuple):
        if dimension not in G.world.dimensions: return
        if chunk not in G.world.dimensions[dimension].chunks: return
        chunk_instance: world.Chunk.Chunk = G.world.dimensions[dimension].chunks[chunk]
        palette = []
        blocks = {}
        for position in chunk_instance.world:
            block = chunk_instance.world[position]
            block_data = {"custom": block.save(), "name": block.NAME, "shown": any(block.face_state.faces.values())}
            if block.get_inventories() is not None:
                block_data["inventories"] = {}
                for i, inventory in enumerate(block.get_inventories()):
                    path = "blockinv/{}_{}_{}/{}".format(*position, i)
                    savefile.dump(None, "minecraft:inventory", inventory=inventory, path=path)
                    block_data["inventories"].append(path)
            if block_data in palette:
                blocks[position] = palette.index(block_data)
            else:
                blocks[position] = len(palette)
                palette.append(block_data)
        landmass_map = chunk_instance.get_value("landmassmap")
        temperature_map = chunk_instance.get_value("temperaturemap")
        biome_map = chunk_instance.get_value("biomemap")
        height_map = chunk_instance.get_value("heightmap")
        data = {
            "version": savefile.version,
            "dimension": dimension,
            "position": chunk,
            "blocks": blocks,
            "block_palette": palette,
            "generated": chunk_instance.generated,
            "maps": {
                "landmass": landmass_map,
                "temperature": temperature_map,
                "biome": biome_map,
                "height": height_map
            }
        }
        savefile.dump_file_pickle("dim/{}/{}_{}.chunk".format(dimension, *chunk), data)

