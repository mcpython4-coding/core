"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""

import random
import opensimplex
import mcpython.common.event.EventHandler

from mcpython import shared as G
from mcpython.server.worldgen.layer.Layer import Layer, LayerConfig


@G.worldgenerationhandler
class DefaultBedrockLayer(Layer):
    """
    Class for generating the bedrock layer
    How does it work?
    It firstly generates with the current random seed an new seed for later
    Than, it random.seed()s based on an noise and the chunk position
    Than, for each xz position, the following is done:
        - add lowest layer
        - for each of the next layers, random.randint() is used to determine if to generate bedrock or not
    For cleanup, the previous generated seed is random.seed()ed for returning to an independent seed
    """

    noise: opensimplex.OpenSimplex = None

    @classmethod
    def update_seed(cls):
        seed = G.world.config["seed"]
        cls.noise = opensimplex.OpenSimplex(seed=seed * 100)

    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "bedrock_chance"):
            config.bedrock_chance = 3

    NAME = "minecraft:bedrock_default"

    @classmethod
    def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        old_re_seed = random.random()
        random.seed(cls.noise.noise2d(*chunk.position))

        for x in range(chunk.position[0] * 16, chunk.position[0] * 16 + 16):
            for z in range(chunk.position[1] * 16, chunk.position[1] * 16 + 16):
                reference.schedule_block_add((x, 0, z), "minecraft:bedrock")
                for y in range(1, 5):
                    if random.randint(1, config.bedrock_chance) == 1:
                        reference.schedule_block_add((x, y, z), "minecraft:bedrock")

        random.seed(old_re_seed)


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "seed:set", DefaultBedrockLayer.update_seed
)
