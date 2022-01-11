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
import asyncio
import itertools
import random

import mcpython.common.world.Chunk
import mcpython.server.worldgen.feature.IFeature
import mcpython.server.worldgen.noise.INoiseImplementation
import mcpython.server.worldgen.noise.NoiseManager
from mcpython import shared
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@shared.world_generation_handler
class DefaultFeatureLayer(ILayer):
    DEPENDS_ON = ["minecraft:biome_map_default", "minecraft:heightmap_default"]

    NAME = "minecraft:feature_default"

    placement_noise = (
        mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
            NAME,
            scale=1,
            dimensions=3,
            octaves=3,
            merger=mcpython.server.worldgen.noise.INoiseImplementation.INNER_MERGE,
        )
    )

    @classmethod
    async def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        cx *= 16
        cz *= 16

        await asyncio.gather(
            *(
                cls.generate_position(
                    cx + 4 * x,
                    cz + 4 * z,
                    reference,
                    config,
                    i,
                )
                for i, (x, z) in enumerate(itertools.product(range(0, 4), range(0, 4)))
            )
        )

    @classmethod
    async def generate_position(cls, x, z, reference, config, index: int):
        chunk = reference.chunk

        # todo: rename to structure blocking info or something similar
        treemap = chunk.get_map("minecraft:feature_map")

        # the various maps
        biome = shared.biome_handler.biomes[
            chunk.get_map("minecraft:biome_map").get_at_xyz(x, 0, z)
        ]
        height = chunk.get_map("minecraft:height_map").get_at_xz(x, z)[0][1]

        # and now iterate over all features
        for group in biome.FEATURES_SORTED:
            count, total_weight, weights, features = biome.FEATURES_SORTED[group]
            if type(count) == tuple:
                count = random.randint(*count)

            if count <= 0 or len(features) == 0:
                continue

            for c in range(count):
                # should we use this position?
                # todo: make position in chunk noise based, like a noise of size, and _ as index in y direction,
                #   and x, z the chunk position, deciding the x and z coordinates in that chunk

                sector = cls.placement_noise.calculate_position((x // 16, z // 16, c))

                if round(sector * 16) != index:
                    continue

                offset = random.randint(0, 3), random.randint(0, 3)

                # Use one random feature todo: make noise based
                feature_def: mcpython.server.worldgen.feature.IFeature.FeatureDefinition = random.choices(
                    features, cum_weights=weights, k=1
                )[
                    0
                ]

                px, py, pz = (
                    x + offset[0],
                    feature_def.spawn_point.select(x, z, height, biome),
                    z + offset[1],
                )

                if treemap.overlaps_with_region((px, py, pz), (px, py, pz)):
                    return  # is a tree nearby?

                feature = feature_def.feature
                await feature.place_array(
                    reference,
                    px,
                    py,
                    pz,
                    feature_def.config,
                )

                # todo: add a getter to the feature for the size
                treemap.reserve_region((px, py, pz), (px, py, pz), feature.NAME)
