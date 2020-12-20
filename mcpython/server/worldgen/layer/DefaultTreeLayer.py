"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""

import random

from mcpython import shared as G
import mcpython.common.world.Chunk
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@G.world_generation_handler
class DefaultTreeLayer(ILayer):
    DEPENDS_ON = ["minecraft:biome_map_default", "minecraft:heightmap_default"]

    NAME = "minecraft:tree_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        cx *= 16
        cz *= 16
        for x in range(16):
            for z in range(16):
                reference.schedule_invoke(
                    DefaultTreeLayer.generate_position,
                    cx + x,
                    cz + z,
                    reference,
                    config,
                )

    @staticmethod
    def generate_position(x, z, reference, config):
        chunk = reference.chunk
        treemap = chunk.get_value("tree_blocked")
        if (x, z) in treemap:
            return  # is an tree nearby?
        biome = G.biome_handler.biomes[chunk.get_value("minecraft:biome_map")[(x, z)]]
        height = chunk.get_value("heightmap")[(x, z)][0][1]
        trees = biome.get_trees()
        # todo: make noise-based
        for IFeature, chance in trees:
            if random.randint(1, chance) == 1:
                IFeature.place(chunk.dimension, x, height + 1, z)
                for dx in range(-2, 3):
                    for dz in range(-2, 3):
                        treemap.append((x + dx, z + dz))
                return


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "tree_blocked", DefaultTreeLayer, []
)
