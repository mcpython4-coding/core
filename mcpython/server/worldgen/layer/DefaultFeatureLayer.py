"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""

import random

from mcpython import shared
import mcpython.common.world.Chunk
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig
import mcpython.server.worldgen.feature.IFeature


@shared.world_generation_handler
class DefaultFeatureLayer(ILayer):
    DEPENDS_ON = ["minecraft:biome_map_default", "minecraft:heightmap_default"]

    NAME = "minecraft:feature_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, reference):
        chunk = reference.chunk
        cx, cz = chunk.position
        cx *= 16
        cz *= 16
        for x in range(16):
            for z in range(16):
                reference.schedule_invoke(
                    DefaultFeatureLayer.generate_position,
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
        biome = shared.biome_handler.biomes[
            chunk.get_value("minecraft:biome_map")[(x, z)]
        ]
        height = chunk.get_value("heightmap")[(x, z)][0][1]
        for group in biome.FEATURES_SORTED:
            count, total_weight, weights, features = biome.FEATURES_SORTED[group]
            if type(count) == tuple:
                count = random.randint(*count)
            if count <= 0 or len(features) == 0:
                continue
            for _ in range(count):
                if random.randint(1, 256) != 1:
                    continue
                feature_def: mcpython.server.worldgen.feature.IFeature.FeatureDefinition = random.choices(
                    features, cum_weights=weights, k=1
                )[
                    0
                ]
                feature = feature_def.feature
                feature.place_array(
                    reference,
                    x,
                    feature_def.spawn_point.select(x, z, height, biome),
                    z,
                    feature_def.config,
                )


mcpython.common.world.Chunk.Chunk.add_default_attribute(
    "tree_blocked", DefaultFeatureLayer, []
)
