"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import time
import typing

from mcpython import shared, logger
import mcpython.common.mod.ModMcpython
import mcpython.common.world.Chunk
import mcpython.common.world.AbstractInterface
import mcpython.common.world.Dimension
import mcpython.server.worldgen.layer.Layer
import mcpython.server.worldgen.mode
import mcpython.server.worldgen.WorldGenerationTaskArrays


class WorldGenerationHandler:
    """
    Main handler instance for world generation
    """

    def __init__(self):
        self.layers = {}
        self.features = {}
        self.configs = {}
        self.enable_generation = False  # if world gen should be enabled
        self.enable_auto_gen = (
            False  # if chunks around the player should be generated when needed
        )
        self.task_handler = (
            mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandler()
        )

    def add_chunk_to_generation_list(
        self,
        chunk,
        dimension=None,
        force_generate=False,
        immediate=False,
    ):
        """
        adds chunk schedule to the system
        will set the loaded-flag of the chunk during the process
        will schedule the internal _add_chunk function
        :param chunk: the chunk
        :param dimension: optional: if chunk is tuple, if another dim than active should be used
        :param force_generate: if generation should take place also when auto-gen is disabled
        :param immediate: if _add_chunk should be called immediate or not [can help in cases where TaskHandler stops
            running tasks when in-generation progress]
        """
        if not self.enable_auto_gen and not force_generate:
            return
        if type(chunk) == tuple:
            if dimension is None:
                chunk = shared.world.get_active_dimension().get_chunk(
                    *chunk, generate=False
                )
            else:
                chunk = shared.world.dimensions[dimension].get_chunk(
                    *chunk, generate=False
                )
        if immediate:
            self._add_chunk(chunk)
        else:
            self.task_handler.schedule_invoke(chunk, self._add_chunk, chunk)
        chunk.loaded = True

    def _add_chunk(self, chunk: mcpython.common.world.AbstractInterface.IChunk):
        """
        internal implementation of the chunk generation code
        :param chunk: the chunk to schedule
        """
        dimension = chunk.dimension
        config_name = dimension.worldgenerationconfig["configname"]

        if config_name not in self.configs:
            return  # no config found means no generation

        config = self.configs[config_name]
        reference = mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference(
            self.task_handler, chunk
        )
        for layer_name in config["layers"]:
            reference.schedule_invoke(
                self.layers[layer_name].add_generate_functions_to_chunk,
                chunk.dimension.worldgenerationconfigobjects[layer_name],
                reference,
            )

    def process_one_generation_task(self, **kwargs):  # todo: remove
        if not self.enable_generation:
            return
        self.task_handler.process_one_task(**kwargs)

    def setup_dimension(self, dimension, config=None):
        config_name = dimension.worldgenerationconfig["configname"]
        if config_name is None:
            return  # empty dimension
        for layer_name in self.configs[config_name]["layers"]:
            layer = self.layers[layer_name]
            if config is None or layer_name not in config:
                cconfig = mcpython.server.worldgen.layer.Layer.LayerConfig(
                    **(
                        dimension.worldgenerationconfig[layer_name]
                        if layer_name in dimension.worldgenerationconfig
                        else {}
                    )
                )
                cconfig.dimension = dimension.id
            else:
                cconfig = config[layer_name]
            layer.normalize_config(cconfig)
            dimension.worldgenerationconfigobjects[layer_name] = cconfig
            cconfig.layer = layer

    def generate_chunk(
        self,
        chunk: typing.Union[mcpython.common.world.AbstractInterface.IChunk, tuple],
        dimension=None,
        check_chunk=True,
    ):
        if not self.enable_generation:
            return
        if check_chunk and chunk.generated:
            return
        if type(chunk) == tuple:
            if dimension is None:
                chunk = shared.world.get_active_dimension().get_chunk(
                    *chunk, generate=False
                )
            elif type(dimension) == int:
                chunk = shared.world.dimensions[dimension].get_chunk(
                    *chunk, generate=False
                )
            else:
                chunk = dimension.get_chunk(*chunk, generate=False)
        chunk.loaded = True
        logger.println("generating", chunk.position)
        dimension = chunk.dimension
        configname = dimension.worldgenerationconfig["configname"]
        config = self.configs[configname]
        if "on_chunk_generate_pre" in config:
            config["on_chunk_generate_pre"](chunk.position[0], chunk.position[1], chunk)
        # m = len(config["layers"])
        handler = mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference(
            self.task_handler, chunk
        )
        for i, layername in enumerate(config["layers"]):
            # logger.println("\rgenerating layer {} ({}/{})".format(layername, i + 1, m), end="")
            layer = self.layers[layername]
            layer.add_generate_functions_to_chunk(
                dimension.worldgenerationconfigobjects[layername], handler
            )
            shared.worldgenerationhandler.task_handler.process_tasks()
        logger.println("\r", end="")
        shared.eventhandler.call("worldgen:chunk:finished", chunk)
        chunk.generated = True
        chunk.loaded = True

    def register_layer(self, layer: mcpython.server.worldgen.layer.Layer.Layer):
        self.layers[layer.NAME] = layer  # todo: make more fancy

    def register_feature(self, decorator):
        pass  # todo: implement

    def register_world_gen_config(self, name: str, layerconfig: dict):
        self.configs[name] = layerconfig

    def __call__(self, data: str or mcpython.server.worldgen.layer.Layer, config=None):
        if type(data) == dict:
            self.register_world_gen_config(data, config)
        elif issubclass(data, mcpython.server.worldgen.layer.Layer.Layer):
            self.register_layer(data)
        elif issubclass(data, object):
            self.register_feature(data)
        else:
            raise TypeError("unknown data type")
        return data


shared.worldgenerationhandler = WorldGenerationHandler()


def load_layers():
    from .layer import (
        DefaultBedrockLayer,
        DefaultBiomeLayer,
        DefaultHeightMapLayer,
        DefaultLandMassLayer,
        DefaultStonePlacementLayer,
        DefaultTemperatureLayer,
        DefaultTopLayerLayer,
        DefaultTreeLayer,
    )


def load_modes():
    from .mode import (
        DefaultOverWorldGenerator,
        DebugOverWorldGenerator,
        DefaultNetherWorldGenerator,
    )


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:layer", load_layers, info="loading generation layers"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:mode", load_modes, info="loading generation modes"
)
