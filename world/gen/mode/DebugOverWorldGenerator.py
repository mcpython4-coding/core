"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.Registry
import math
import util.math
import mod.ModMcpython
import event.EventHandler


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


def chunk_generate(chunk):
    cx, cz = chunk.position
    if G.world.get_active_dimension().worldgenerationconfig["configname"] != "debug_overworld": return

    if (cx, cz) in blockinfo.TABLE:
        heigthmap = chunk.get_value("heightmap")
        blockmap = blockinfo.TABLE[(cx, cz)]
        for x, z in blockmap.keys():
            block, state = blockmap[(x, z)]
            block = chunk.add_block((x, 10, z), block, block_update=False)
            block.set_model_state(state)
            heigthmap[(x, z)] = [(0, 10)]


config = {"layers": []}

G.worldgenerationhandler.register_world_gen_config("debug_overworld", config)

mod.ModMcpython.mcpython.eventbus.subscribe("stage:post", blockinfo.construct, info="constructing debug world info")
event.EventHandler.PUBLIC_EVENT_BUS.subscribe("worldgen:chunk:finished", chunk_generate)

