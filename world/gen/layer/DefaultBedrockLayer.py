"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""

from world.gen.layer.Layer import Layer, LayerConfig
import globals as G
import random


@G.worldgenerationhandler
class DefaultBedrockLayer(Layer):
    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "bedrockchance"):
            config.bedrockchance = 3

    NAME = "bedrock_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultBedrockLayer.generate_bedrock_base, [chunk], {}])
        chunk.chunkgenerationtasks.append([DefaultBedrockLayer.generate_bedrock_top, [chunk, config], {}])

    @staticmethod
    def generate_bedrock_base(chunk):
        for x in range(chunk.position[0]*16, chunk.position[0]*16+16):
            for z in range(chunk.position[1]*16, chunk.position[1]*16+16):
                chunk.add_add_block_gen_task((x, 0, z), "minecraft:bedrock")

    @staticmethod
    def generate_bedrock_top(chunk, config):
        for x in range(chunk.position[0]*16, chunk.position[0]*16+16):
            for z in range(chunk.position[1]*16, chunk.position[1]*16+16):
                for y in range(1, 5):
                    if random.randint(1, config.bedrockchance) == 1:
                        chunk.add_add_block_gen_task((x, y, z), "minecraft:bedrock")



