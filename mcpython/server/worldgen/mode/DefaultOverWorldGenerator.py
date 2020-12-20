"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.server.worldgen.mode.IWorldGenConfig


class DefaultOverworldGenerator(
    mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig
):
    NAME = "minecraft:default_overworld"
    DIMENSION = "minecraft:overworld"

    LAYERS = [
        "minecraft:landmass_default",
        "minecraft:temperature_map",
        "minecraft:biome_map_default",
        "minecraft:heightmap_default",
        "minecraft:bedrock_default",
        "minecraft:stone_default",
        "minecraft:top_layer_default",
        "minecraft:feature_default",
    ]

    BIOMES = {
        "land": {
            2.0: ["minecraft:dessert"],
            0.8: ["minecraft:plains"],
            0.2: ["minecraft:mountains"],
        }
    }

    LANDMASSES = ["land"]

    BIOME_SOURCE = mcpython.server.worldgen.mode.IWorldGenConfig.DefaultBiomeSource

    GENERATES_START_CHEST = True


G.world_generation_handler.register_world_gen_config(DefaultOverworldGenerator)
