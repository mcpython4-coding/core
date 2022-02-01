"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.server.worldgen.noise.NoiseManager
from mcpython import shared
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@shared.world_generation_handler
class DefaultBiomeMapLayer(ILayer):
    """
    Layer for calculating which biomes to generate
    """

    NAME = "minecraft:biome_map_default"
    DEPENDS_ON = ["minecraft:landmass_default", "minecraft:temperature_map"]

    noises: typing.List[
        mcpython.server.worldgen.noise.NoiseManager.INoiseImplementation
    ] = [
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_1", dimensions=4, scale=10**10
        ),
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_2", dimensions=4, scale=10**10
        ),
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME + "_3", dimensions=4, scale=10**10
        ),
    ]

    @classmethod
    async def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.get_position()

        # The various chunk maps needed
        biome_map = chunk.get_map("minecraft:biome_map")
        land_map = chunk.get_map("minecraft:landmass_map")
        temperature_map = chunk.get_map("minecraft:temperature_map")

        # Now iterate over all positions
        # todo: use a map calculation
        for x in range(cx * 16, cx * 16 + 16, 4):
            for z in range(cz * 16, cz * 16 + 16, 4):
                biome_map.set_at_xyz(
                    x,
                    0,
                    z,
                    config.world_generator_config.BIOME_SOURCE.get_biome_at(
                        x,
                        z,
                        cls.noises,
                        land_map.get_at_xz(x, z),
                        config,
                        temperature_map.get_at_xz(x, z),
                    ),
                )
