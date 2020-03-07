import storage.serializer.IDataSerializer
import globals as G
import world.Chunk
import util.enums


@G.registry
class Chunk(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:chunk"

    @classmethod
    def load(cls, savefile, dimension: int, chunk: tuple):
        if dimension not in G.world.dimensions: return
        chunk_instance: world.Chunk.Chunk = G.world.dimensions[dimension].get_chunk(*chunk, generate=False)
        chunk_instance.loaded = True
        data = savefile.access_file_pickle("dim/{}/{}_{}.chunk".format(dimension, *chunk_instance))
        if data is None: return
        if data["version"] != savefile.version:
            savefile.upgrade("minecraft:chunk", version=data["version"], dimension=dimension, chunk=chunk)
            data = savefile.access_file_pickle("dim/{}/{}_{}.chunk".format(dimension, *chunk_instance))
        chunk_instance.generated = data["generated"]
        for position in data["blocks"]:
            d = data["palette"][data["blocks"][position]]
            block = chunk_instance.add_block(position, d["name"])
            block.block_state = d["block_state"]
            block.load(d["custom"])

    @classmethod
    def save(cls, data, savefile, dimension: int, chunk: tuple):
        if dimension not in G.world.dimensions: return
        if chunk not in G.world.dimensions[dimension].chunks: return
        chunk_instance: world.Chunk.Chunk = G.world.dimensions[dimension].chunks[chunk]
        if chunk_instance.loaded: return
        palette = []
        blocks = {}
        for position in chunk_instance.world:
            block = chunk_instance.world[position]
            block_data = {"custom": block.save(), "name": block.NAME, "block_state": block.block_state,
                          "faces": [block.face_state.faces[e] for e in util.enums.EnumSide.iterate()]}
            if block_data in palette:
                blocks[position] = palette.index(block_data)
            else:
                blocks[position] = len(palette)
                palette.append(block_data)
        data = {
            "version": savefile.version,
            "dimension": dimension,
            "position": chunk,
            "blocks": blocks,
            "block_palette": palette,
            "generated": chunk_instance.generated
        }
        savefile.dump_file_pickle("dim/{}/{}_{}.chunk".format(dimension, *chunk), data)

