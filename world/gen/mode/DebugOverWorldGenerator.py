"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import event.Registry
import math
import util.math


class blockinfo:

    TABLE = {}  # {chunk: tuple<x, z> -> {position<x,z> -> blockname}}

    @classmethod
    def construct(cls):
        BLOCKS: event.Registry.Registry = G.registry.get_by_name("block")

        blocktable = BLOCKS.registered_objects
        blocktable.sort(key=lambda x: x.get_name())
        blocklist = []
        for block in blocktable:
            for state in block.get_all_model_states():
                blocklist.append((block, state))

        size = math.ceil(len(blocklist) ** 0.5)
        hsize = size // 2 + 1

        rx, ry = -hsize, -hsize

        for block, state in blocklist:
            x, y = rx * 4, ry * 4
            chunk = util.math.sectorize((x, 0, y))
            cls.TABLE.setdefault(chunk, {})[(x, y)] = (block.get_name(), state)
            rx += 1
            if x >= hsize:
                ry += 1
                rx = -hsize


def chunk_generate(cx, cz, chunk):
    if (cx, cz) in blockinfo.TABLE:
        heigthmap = chunk.get_value("heightmap")
        blockmap = blockinfo.TABLE[(cx, cz)]
        for x, z in blockmap.keys():
            block, state = blockmap[(x, z)]
            chunk.add_add_block_gen_task((x, 10, z), block, kwargs={"state": state})
            heigthmap[(x, z)] = [(0, 10)]


config = {"layers": [], "on_chunk_generate_pre": chunk_generate}

G.worldgenerationhandler.register_world_gen_config("debug_overworld", config)

