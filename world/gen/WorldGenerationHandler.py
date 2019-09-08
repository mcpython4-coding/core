"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import world.gen.layer.Layer
import world.gen.mode
import world.Dimension
import world.Chunk


class WorldGenerationHandler:
    def __init__(self):
        self.layers = {}
        self.features = {}
        self.configs = {}
        self.enable_generation = False

    def setup_dimension(self, dimension, config=None):
        configname = dimension.worldgenerationconfig["configname"]
        for layername in self.configs[configname]["layers"]:
            layer = self.layers[layername]
            if config is None or layername not in config:
                cconfig = world.gen.layer.Layer.LayerConfig(**dimension.worldgenerationconfig[layername]
                    if layername in dimension.worldgenerationconfig else {})
                cconfig.dimension = dimension.id
            else:
                cconfig = config[layername]
            layer.normalize_config(cconfig)
            dimension.worldgenerationconfigobjects[layername] = cconfig
            cconfig.layer = layer

    def generate_chunk(self, chunk: world.Chunk.Chunk):
        if not self.enable_generation or chunk.is_ready:
            return
        print("generating", chunk.position)
        dimension = chunk.dimension
        configname = dimension.worldgenerationconfig["configname"]
        m = len(self.configs[configname]["layers"])
        for i, layername in enumerate(self.configs[configname]["layers"]):
            print("\rgenerating layer {} ({}/{})".format(layername, i+1, m), end="")
            layer = self.layers[layername]
            layer.add_generate_functions_to_chunk(dimension.worldgenerationconfigobjects[layername], chunk)
            G.world.process_entire_queue()
        print("\r", end="")

    def register_layer(self, layer: world.gen.layer.Layer.Layer):
        # print(layer, layer.get_name())
        self.layers[layer.get_name()] = layer

    def register_feature(self, decorator):
        pass

    def register_world_gen_config(self, name: str, layerconfig: dict):
        self.configs[name] = layerconfig

    def __call__(self, data: str or world.gen.layer.Layer, config=None):
        if type(data) == dict:
            self.register_world_gen_config(data, config)
        elif issubclass(data, world.gen.layer.Layer.Layer):
            self.register_layer(data)
        elif issubclass(data, object):
            self.register_feature(data)
        else:
            raise TypeError("unknown data type")
        return data


G.worldgenerationhandler = WorldGenerationHandler()

from world.gen.layer import (DefaultBedrockLayer, DefaultLandMassLayer, DefaultTemperatureLayer, DefaultBiomeLayer,
                             DefaultHeightMapLayer, DefaultStonePlacementLayer, DefaultTopLayerLayer, DefaultTreeLayer)
from world.gen.mode import DefaultOverWorldGenerator
