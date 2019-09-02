"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G


class LayerConfig:
    def __init__(self, *config, **cconfig):
        self.config = config
        self.layer = None
        for key in cconfig.keys():
            setattr(self, key, cconfig[key])
        self.dimension = None


class Layer:
    @staticmethod
    def normalize_config(config: LayerConfig):
        pass

    @staticmethod
    def get_name() -> str:
        raise NotImplementedError()

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, chunk):
        pass

