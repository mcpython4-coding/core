"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import math

from mcpython import shared as G
import mcpython.common.event.EventHandler
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython
import mcpython.util.math


class Blockinfo:
    TABLE = {}  # {chunk: tuple<x, z> -> {position<x,z> -> blockname}}

    @classmethod
    def construct(cls):
        BLOCKS: mcpython.common.event.Registry.Registry = G.registry.get_by_name(
            "block"
        )

        blocktable = list(BLOCKS.entries.values())
        blocktable.sort(key=lambda x: x.NAME)
        blocklist = []
        for block in blocktable:
            for state in block.DEBUG_WORLD_BLOCK_STATES:
                blocklist.append((block, state))

        size = math.ceil(len(blocklist) ** 0.5)
        hsize = size // 2 + 1

        rx, ry = -hsize, -hsize

        for block, state in blocklist:
            x, y = rx * 4, ry * 4
            chunk = mcpython.util.math.positionToChunk((x, 0, y))
            cls.TABLE.setdefault(chunk, {})[(x, y)] = (block.NAME, state)
            rx += 1
            if x >= hsize:
                ry += 1
                rx = -hsize


def chunk_generate(chunk):
    cx, cz = chunk.position
    if (
        G.world.get_active_dimension().worldgenerationconfig["configname"]
        != "debug_overworld"
    ):
        return

    if (cx, cz) in Blockinfo.TABLE:
        heigthmap = chunk.get_value("heightmap")
        blockmap = Blockinfo.TABLE[(cx, cz)]
        for x, z in blockmap.keys():
            block, state = blockmap[(x, z)]
            block = chunk.add_block((x, 10, z), block, block_update=False)
            block.set_model_state(state)
            block.face_state.update()
            heigthmap[(x, z)] = [(0, 30)]
        for x in range(16):
            for z in range(16):
                chunk.add_block((cx * 16 + x, 5, cz * 16 + z), "minecraft:barrier")

    if G.world.get_active_player().gamemode != 3:
        G.world.get_active_player().set_gamemode(3)
    G.world.get_active_player().flying = True


config = {"layers": []}

G.worldgenerationhandler.register_world_gen_config("debug_overworld", config)

mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:post", Blockinfo.construct, info="constructing debug world info"
)
mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "worldgen:chunk:finished", chunk_generate
)
