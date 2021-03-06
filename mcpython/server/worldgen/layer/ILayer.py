"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.event.Registry
import mcpython.common.world.AbstractInterface


class LayerConfig:
    def __init__(self, *config, **attr_config):
        self.config = config
        self.layer: typing.Optional["ILayer"] = None
        for key in attr_config.keys():
            setattr(self, key, attr_config[key])
        self.dimension: typing.Optional[
            mcpython.common.world.AbstractInterface.IDimension
        ] = None
        self.world_generator_config = None

        self.bedrock_chance = None
        self.max_height_factor = None
        self.masses = None
        self.temperature_max = None
        self.temperature_min = None

    def apply_config(self, attr_config: dict):
        for key in attr_config:
            setattr(self, key, attr_config[key])
        return self


class ILayer(mcpython.common.event.Registry.IRegistryContent):
    """
    Implementation for each layer in generation code.
    An layer is an step in the generation code

    DEPENDS_ON should be an list of other layer names this layer depends on,
    currently not used, but later for parallel world gen
    """

    DEPENDS_ON = []

    @staticmethod
    def normalize_config(config: LayerConfig):
        pass

    NAME = "minecraft:unknown_layer"

    @staticmethod
    def add_generate_functions_to_chunk(config: LayerConfig, reference):
        raise NotImplementedError()
