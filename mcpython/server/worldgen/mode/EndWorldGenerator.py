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


class EndGenerator(mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig):
    NAME = "minecraft:default_end"
    DIMENSION = "minecraft:the_end"

    LAYERS = [
        "minecraft:landmass_default",
        "minecraft:temperature_map",
        "minecraft:biome_map_default",
        "minecraft:heightmap_default",
    ]

    BIOME_SOURCE = mcpython.server.worldgen.mode.IWorldGenConfig.SingleBiomeSource(
        "minecraft:void"
    )


shared.world_generation_handler.register_world_gen_config(EndGenerator)
