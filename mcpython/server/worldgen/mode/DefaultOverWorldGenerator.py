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
import mcpython.server.worldgen.mode.IWorldGenConfig
from mcpython import shared


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
            2.0: [
                "minecraft:dessert",
                "minecraft:dessert_hills",
                "minecraft:dessert_lakes",
            ],
            0.8: ["minecraft:plains", "minecraft:sunflower_plains"],
            0.2: ["minecraft:mountains"],
        }
    }

    LANDMASSES = ["land"]

    BIOME_SOURCE = mcpython.server.worldgen.mode.IWorldGenConfig.DefaultBiomeSource

    GENERATES_START_CHEST = True


shared.world_generation_handler.register_world_gen_config(DefaultOverworldGenerator)
