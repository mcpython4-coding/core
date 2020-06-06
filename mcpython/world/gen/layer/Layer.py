"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.event.Registry


class LayerConfig:
    def __init__(self, *config, **cconfig):
        self.config = config
        self.layer = None
        for key in cconfig.keys():
            setattr(self, key, cconfig[key])
        self.dimension = None


class Layer(mcpython.event.Registry.Registry):
    @staticmethod
    def normalize_config(config: LayerConfig):
        pass

    NAME = "minecraft:unknown_layer"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, reference):
        pass
