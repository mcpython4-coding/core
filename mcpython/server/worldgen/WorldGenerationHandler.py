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
import mcpython.server.worldgen.layer.ILayer
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

    def serialize_chunk_generator_info(self) -> dict:
        data = {}
        for dimension in shared.world.dimensions.values():
            data[dimension.get_name()] = dimension.get_world_generation_config_entry(
                "configname"
            )
        return data

    def deserialize_chunk_generator_info(self, data: dict):
        for dimension in data:
            if dimension not in shared.world.dimensions:
                continue

            shared.world.dimensions[dimension].set_world_generation_config_entry(
                "configname", data[dimension]
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
        dimension = chunk.get_dimension()
        config_name = dimension.get_world_generation_config_entry("configname")

        if config_name not in self.configs[chunk.get_dimension().get_name()]:
            return  # no config found means no generation

        config = self.configs[chunk.get_dimension().get_name()][config_name]
        reference = mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference(
            self.task_handler, chunk
        )
        config.on_chunk_prepare_generation(chunk, reference)
        for layer_name in config.LAYERS:
            if type(layer_name) == str:
                config = chunk.get_dimension().get_world_generation_config_for_layer(
                    layer_name
                )
            else:
                layer_name, config = layer_name
                config = (
                    chunk.get_dimension()
                    .get_world_generation_config_for_layer(layer_name)
                    .apply_config(config)
                )
            reference.schedule_invoke(
                self.layers[layer_name].add_generate_functions_to_chunk,
                config,
                reference,
            )

    def setup_dimension(
        self, dimension: mcpython.common.world.AbstractInterface.IDimension, config=None
    ):
        config_name = dimension.get_world_generation_config_entry("configname")
        if config_name is None:
            return  # empty dimension
        for d in self.configs[dimension.get_name()][config_name].LAYERS:
            if type(d) == str:
                layer_name = d
                cconfig = {}
            else:
                layer_name, cconfig = d
            layer = self.layers[layer_name]
            if config is None or layer_name not in config:
                layer_config = mcpython.server.worldgen.layer.ILayer.LayerConfig(
                    **(
                        dimension.get_world_generation_config_entry(
                            layer_name, default={}
                        )
                    ),
                    **cconfig
                )
                layer_config.dimension = dimension.get_id()
            else:
                layer_config = config[layer_name]
            layer_config.world_generator_config = self.configs[dimension.get_name()][
                config_name
            ]
            layer.normalize_config(layer_config)
            dimension.set_world_generation_config_for_layer(layer_name, layer_config)
            layer_config.layer = layer

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
        config = self.get_current_config(dimension)
        if "on_chunk_generate_pre" in config:
            config["on_chunk_generate_pre"](chunk.position[0], chunk.position[1], chunk)
        # m = len(config["layers"])
        handler = mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference(
            self.task_handler, chunk
        )
        config.on_chunk_prepare_generation(chunk, handler)
        for i, layer_name in enumerate(config["layers"]):
            layer = self.layers[layer_name]
            layer.add_generate_functions_to_chunk(
                dimension.world_generation_config_objects[layer_name], handler
            )
            shared.world_generation_handler.task_handler.process_tasks()
        logger.println("\r", end="")
        self.mark_finished(chunk)
        chunk.generated = True
        chunk.loaded = True

    def get_current_config(
        self, dimension: mcpython.common.world.AbstractInterface.IDimension
    ):
        config_name = dimension.get_world_generation_config_entry("configname")
        return self.configs[dimension.get_name()][config_name]

    def set_current_config(
        self, dimension: mcpython.common.world.AbstractInterface.IDimension, config: str
    ):
        dimension.set_world_generation_config_entry("configname", config)

    def mark_finished(self, chunk: mcpython.common.world.AbstractInterface.IChunk):
        config_name = chunk.get_dimension().get_world_generation_config_entry(
            "configname"
        )
        config = self.configs[chunk.get_dimension().get_name()][config_name]
        shared.event_handler.call("worldgen:chunk:finished", chunk)
        config.on_chunk_generation_finished(chunk)

    def register_layer(self, layer: mcpython.server.worldgen.layer.ILayer.ILayer):
        self.layers[layer.NAME] = layer  # todo: make more fancy

    def register_feature(self, decorator):
        pass  # todo: implement

    def register_world_gen_config(self, instance):
        self.configs.setdefault(instance.DIMENSION, {})[instance.NAME] = instance

    def unregister_world_gen_config(self, instance):
        del self.configs[instance.DIMENSION][instance.NAME]

    def get_world_gen_config(self, dimension: str, name: str):
        return self.configs[dimension][name]

    def __call__(
        self,
        data: typing.Union[str, mcpython.server.worldgen.layer.ILayer.ILayer],
        config=None,
    ):
        if type(data) == dict:
            self.register_world_gen_config(config)
        elif issubclass(data, mcpython.server.worldgen.layer.ILayer.ILayer):
            self.register_layer(data)
        elif issubclass(data, object):
            self.register_feature(data)
        else:
            raise TypeError("unknown data type")
        return data


shared.world_generation_handler = WorldGenerationHandler()


def load_layers():
    from .layer import (
        DefaultBedrockLayer,
        DefaultBiomeLayer,
        DefaultHeightMapLayer,
        DefaultLandMassLayer,
        DefaultStonePlacementLayer,
        DefaultTemperatureLayer,
        DefaultTopLayerLayer,
        DefaultFeatureLayer,
    )


def load_modes():
    from .mode import (
        DefaultOverWorldGenerator,
        DebugOverWorldGenerator,
        DefaultNetherWorldGenerator,
        BiomeGenDebugGenerator,
        AmplifiedWorldGenerator,
        EndWorldGenerator,
    )


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:layer", load_layers, info="loading generation layers"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:mode", load_modes, info="loading generation modes"
)
