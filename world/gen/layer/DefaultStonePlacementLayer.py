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
class DefaultStonePlacementLayer(Layer):
    @staticmethod
    def normalize_config(config: LayerConfig):
        if not hasattr(config, "bedrockchance"):
            config.bedrockchance = 3

    NAME = "stone_default"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        chunk.chunkgenerationtasks.append([DefaultStonePlacementLayer.generate_chunk, [chunk, config], {}])

    @staticmethod
    def generate_chunk(chunk, config):
        for x in range(chunk.position[0]*16, chunk.position[0]*16+16):
            for z in range(chunk.position[1]*16, chunk.position[1]*16+16):
                chunk.chunkgenerationtasks.append([DefaultStonePlacementLayer.generate_xz, [chunk, x, z, config], {}])

    @staticmethod
    def generate_xz(chunk, x, z, config):
        heightmap = chunk.get_value("heightmap")
        height = heightmap[(x, z)][0][1]
        for y in range(1, height+1):
            if not chunk.is_position_blocked((x, y, z)):
                chunk.add_add_block_gen_task((x, y, z), "minecraft:stone", immediate=False)



