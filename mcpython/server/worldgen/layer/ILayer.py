"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.event.api
import mcpython.common.event.Registry
import mcpython.engine.world.AbstractInterface


class LayerConfig:
    def __init__(self, *config, **attr_config):
        self.config = config
        self.layer: typing.Optional["ILayer"] = None
        for key in attr_config.keys():
            setattr(self, key, attr_config[key])
        self.dimension: typing.Optional[
            mcpython.engine.world.AbstractInterface.IDimension
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


class ILayer(mcpython.common.event.api.IRegistryContent):
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
