"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

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
import mcpython.common.event.Registry


class WorldGenerationHandler:
    """
    Main handler instance for world generation
    Stored data for world generation and handles requests for generating chunks
    """

    def __init__(self):
        # registry table for layers
        self.layers = {}

        # a config table: dimension name -> config list
        self.configs = {}

        # if world gen should be enabled
        self.enable_generation = False

        # if chunks around the player should be generated when needed
        self.enable_auto_gen = False

        # the general task handler instance
        self.task_handler = (
            mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandler()
        )

        # the feature registry, replacing old dict stored here
        # has some fancier internals :-)
        self.feature_registry = mcpython.common.event.Registry.Registry(
            "minecraft:world_gen_features",
            ["minecraft:generation_feature"],
            "stage:worldgen:feature",
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
        Adds chunk schedule to the system
        Will set the loaded-flag of the chunk during the process
        Will schedule the internal _add_chunk function
        :param chunk: the chunk
        :param dimension: optional: if chunk is tuple, if another dim than active should be used
        :param force_generate: if generation should take place also when auto-gen is disabled
        :param immediate: if _add_chunk should be called immediate or not [can help in cases where TaskHandler stops
            running tasks when in-generation progress]
        """
        # if we don't want to auto-generate, so check here
        if not self.enable_auto_gen and not force_generate:
            return

        # If it's not an chunk instance, make it one
        if type(chunk) == tuple:
            if dimension is None:
                # todo: is there something better than this / remove this
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
        # read needed information
        dimension = chunk.get_dimension()
        config_name = dimension.get_world_generation_config_entry("configname")

        # no config found means no generation
        if config_name not in self.configs[chunk.get_dimension().get_name()]:
            logger.println("[WARN] skipping generation of chunk {}-{} in dimension {}".format(
                *chunk.get_position(), dimension.get_name()))
            return

        config = self.configs[chunk.get_dimension().get_name()][config_name]

        reference = mcpython.server.worldgen.WorldGenerationTaskArrays.WorldGenerationTaskHandlerReference(
            self.task_handler, chunk
        )
        config.on_chunk_prepare_generation(chunk, reference)

        for layer_name in config.LAYERS:
            # only layer...
            if type(layer_name) == str:
                config = chunk.get_dimension().get_world_generation_config_for_layer(
                    layer_name
                )

            # ... or with config
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
        """
        Sets up the layer configs for the given dimension
        :param dimension: the dimension to use
        :param config: optional additional dict specifying LayerConfig's
        """
        config_name = dimension.get_world_generation_config_entry("configname")
        if config_name is None:
            return  # empty dimension

        for d in self.configs[dimension.get_name()][config_name].LAYERS:
            if type(d) == str:
                layer_name = d
                layer_config = {}
            else:
                layer_name, layer_config = d

            layer = self.layers[layer_name]
            if config is None or layer_name not in config:
                layer_config = mcpython.server.worldgen.layer.ILayer.LayerConfig(
                    **(
                        dimension.get_world_generation_config_entry(
                            layer_name, default={}
                        )
                    ),
                    **layer_config
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
        dimension: typing.Union[mcpython.common.world.AbstractInterface.IDimension, int, str, None] = None,
        check_chunk=True,
    ):
        """
        Generates the chunk in-place
        :param chunk: the chunk, as an instance, or a tuple
        :param dimension: if tuple, specifies the dimension. When still None, the active dimension is used
        :param check_chunk: if the chunk should be checked if its generated or not
        """
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
            elif type(dimension) == str:
                chunk = shared.world.get_dimension(dimension).get_chunk(
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

        self.mark_finished(chunk)
        chunk.generated = True
        chunk.loaded = True

    def get_current_config(
        self, dimension: mcpython.common.world.AbstractInterface.IDimension
    ):
        """
        Helper method for getting the the world generation configuration for a given dimension
        :param dimension: the dimension instance
        todo: allow string and similar
        """
        config_name = dimension.get_world_generation_config_entry("configname")
        return self.configs[dimension.get_name()][config_name]

    def set_current_config(
        self, dimension: mcpython.common.world.AbstractInterface.IDimension, config: str
    ):
        """
        Writes a config name as the given into an dimension object
        :param dimension: the dimension
        :param config: the config name
        """
        dimension.set_world_generation_config_entry("configname", config)

    def mark_finished(self, chunk: mcpython.common.world.AbstractInterface.IChunk):
        """
        Internal helper for marking a chunk as finished. Will call the needed events.
        :param chunk: the chunk instance
        """
        config_name = chunk.get_dimension().get_world_generation_config_entry(
            "configname"
        )
        config = self.configs[chunk.get_dimension().get_name()][config_name]
        shared.event_handler.call("worldgen:chunk:finished", chunk)
        config.on_chunk_generation_finished(chunk)

    def register_layer(self, layer: typing.Type[mcpython.server.worldgen.layer.ILayer.ILayer]):
        """
        Registers a new layer object into the system
        :param layer: the layer instance
        todo: make more fancy
        """
        self.layers[layer.NAME] = layer

    def register_world_gen_config(self, instance):
        self.configs.setdefault(instance.DIMENSION, {})[instance.NAME] = instance

    def unregister_world_gen_config(self, instance):
        del self.configs[instance.DIMENSION][instance.NAME]

    def get_world_gen_config(self, dimension: str, name: str):
        return self.configs[dimension][name]

    def __call__(
        self,
        data: typing.Type[mcpython.server.worldgen.layer.ILayer.ILayer],
    ):
        if issubclass(data, mcpython.server.worldgen.layer.ILayer.ILayer):
            self.register_layer(data)
        else:
            raise TypeError("unknown data type", type(data))
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


def load_features():
    from .feature import (
        CactusFeature,
        DessertTempleFeature,
        DessertWellFeature,
        FossileFeature,
        OakTreeFeature,
        PillagerOutpostDefinition,
        PlantFeature,
        SpruceTreeFeature,
    )
    from .feature.village import VillageFeatureDefinition


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:layer", load_layers, info="loading generation layers"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:mode", load_modes, info="loading generation modes"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:feature", load_features, info="loading world gen features"
)
