"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.Registry


class LayerConfig:
    def __init__(self, *config, **cconfig):
        self.config = config
        self.layer = None
        for key in cconfig.keys():
            setattr(self, key, cconfig[key])
        self.dimension = None


class Layer(event.Registry.Registry):
    @staticmethod
    def normalize_config(config: LayerConfig):
        pass

    NAME = "minecraft:unknown_layer"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        pass

