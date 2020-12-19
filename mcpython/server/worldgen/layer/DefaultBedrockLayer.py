"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""

import mcpython.server.worldgen.noise.NoiseManager

from mcpython import shared
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@shared.world_generation_handler
class DefaultBedrockILayer(ILayer):
    """
    Class for generating the bedrock layer
    """

    NAME = "minecraft:bedrock_default"

    noise = mcpython.server.worldgen.noise.NoiseManager.manager.create_noise_instance(
        NAME, dimensions=3, scale=0.1
    )

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "bedrock_chance"):
            config.bedrock_chance = 3

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        x, z = chunk.position[0] * 16, chunk.position[1] * 16
        noise_map = cls.noise.calculate_area((x, 1, z), (x + 16, 5, z + 16))

        for (x, y, z), v in noise_map:
            if v * config.bedrock_chance <= 1:
                reference.schedule_block_add((x, y, z), "minecraft:bedrock")

        for x in range(chunk.position[0] * 16, chunk.position[0] * 16 + 16):
            for z in range(chunk.position[1] * 16, chunk.position[1] * 16 + 16):
                reference.schedule_block_add((x, 0, z), "minecraft:bedrock")
