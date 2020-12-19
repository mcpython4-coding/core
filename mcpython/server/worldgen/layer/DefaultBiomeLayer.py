"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.server.worldgen.noise.NoiseManager

from mcpython import shared as G
import mcpython.common.event.EventHandler
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig
import mcpython.common.world.Chunk
import mcpython.common.world.AbstractInterface


@G.world_generation_handler
class DefaultBiomeMapLayer(ILayer):
    NAME = "minecraft:biome_map_default"
    DEPENDS_ON = ["minecraft:landmass_default"]

    noises: typing.List[
        mcpython.server.worldgen.noise.NoiseManager.INoiseImplementation
    ] = [
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_1", dimensions=4, scale=10 ** 10
        ),
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_2", dimensions=4, scale=10 ** 10
        ),
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_3", dimensions=4, scale=10 ** 10
        ),
    ]

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        biome_map = chunk.get_value("minecraft:biome_map")
        land_map = chunk.get_value("minecraft:landmass_map")
        temperature_map = chunk.get_value("minecraft:temperature_map")
        for x in range(cx * 16, cx * 16 + 16):
            for z in range(cz * 16, cz * 16 + 16):
                biome_map[
                    (x, z)
                ] = config.world_generator_config.BIOME_SOURCE.get_biome_at(
                    x, z, cls.noises, land_map[(x, z)], config, temperature_map[(x, z)]
                )
        chunk.set_value("minecraft:biome_map", biome_map)


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "minecraft:biome_map", DefaultBiomeMapLayer, {}
)
