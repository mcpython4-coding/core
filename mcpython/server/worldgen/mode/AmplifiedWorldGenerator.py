"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.server.worldgen.mode.IWorldGenConfig
import mcpython.server.worldgen.mode.DefaultOverWorldGenerator


class AmplifiedOverworldGenerator(
    mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig
):
    NAME = "minecraft:amplified_overworld"
    DIMENSION = "minecraft:overworld"

    LAYERS = [
        "minecraft:landmass_default",
        "minecraft:temperature_map",
        "minecraft:biome_map_default",
        ("minecraft:heightmap_default", {"max_height_factor": 2}),
        "minecraft:bedrock_default",
        "minecraft:stone_default",
        "minecraft:top_layer_default",
        "minecraft:feature_default",
    ]

    BIOMES = (
        mcpython.server.worldgen.mode.DefaultOverWorldGenerator.DefaultOverworldGenerator.BIOMES
    )
    LANDMASSES = (
        mcpython.server.worldgen.mode.DefaultOverWorldGenerator.DefaultOverworldGenerator.LANDMASSES
    )
    BIOME_SOURCE = mcpython.server.worldgen.mode.IWorldGenConfig.DefaultBiomeSource
    GENERATES_START_CHEST = True


shared.world_generation_handler.register_world_gen_config(AmplifiedOverworldGenerator)
