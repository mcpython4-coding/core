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


class NetherWorldGenerator(
    mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig
):
    NAME = "minecraft:nether_generator"
    DIMENSION = "minecraft:the_nether"

    LAYERS = [
        "minecraft:landmass_default",
        "minecraft:temperature_map",
        "minecraft:biome_map_default",
        "minecraft:heightmap_default",
    ]

    BIOME_SOURCE = mcpython.server.worldgen.mode.IWorldGenConfig.SingleBiomeSource(
        "minecraft:void"
    )


shared.world_generation_handler.register_world_gen_config(NetherWorldGenerator)
