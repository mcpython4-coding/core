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

import mcpython.server.worldgen.noise.NoiseManager
from mcpython import shared
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@shared.world_generation_handler
class DefaultBedrockLayer(ILayer):
    """
    Class for generating the bedrock layer
    """

    NAME = "minecraft:bedrock_default"

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME, dimensions=3, scale=0.1
    )

    @staticmethod
    def normalize_config(config: LayerConfig):
        if config.bedrock_chance is None:
            config.bedrock_chance = 3

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        x, z = chunk.position[0] * 16, chunk.position[1] * 16

        # The map of noises, for calculation if to generate bedrock or not
        noise_map = cls.noise.calculate_area((x, 1, z), (x + 16, 5, z + 16))

        # Use this map and generate bedrock
        for (x, y, z), v in noise_map:
            if v * config.bedrock_chance <= 1:
                reference.schedule_block_add((x, y, z), "minecraft:bedrock")

        # And generate the lowest layer
        for x in range(chunk.position[0] * 16, chunk.position[0] * 16 + 16):
            for z in range(chunk.position[1] * 16, chunk.position[1] * 16 + 16):
                reference.schedule_block_add((x, 0, z), "minecraft:bedrock")
