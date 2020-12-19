"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""

import random

import mcpython.server.worldgen.noise.NoiseManager

from mcpython import shared as G
import mcpython.common.event.EventHandler
import mcpython.common.world.Chunk
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@G.world_generation_handler
class DefaultHeightMapILayer(ILayer):
    NAME = "minecraft:heightmap_default"
    DEPENDS_ON = ["minecraft:biome_map_default"]

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME, scale=10 ** 2, dimensions=2
    )

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        heightmap = chunk.get_value("heightmap")
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        noise_map = cls.noise.calculate_area((x, z), (x + 16, z + 16))
        for (x, z), v in noise_map:
            heightmap[(x, z)] = cls.get_height_at(chunk, x, z, v)

    @classmethod
    def get_height_at(cls, chunk, x, z, v) -> list:
        biome_map = chunk.get_value("minecraft:biome_map")
        biome = G.biome_handler.biomes[biome_map[(x, z)]]
        r = biome.get_height_range()
        v *= r[1] - r[0]
        v += r[0]
        info = [(1, round(v))]
        return info


authcode = mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "heightmap", DefaultHeightMapILayer, {}
)
