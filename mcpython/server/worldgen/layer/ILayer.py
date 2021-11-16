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
    """
    The configuration object for world generation layers.
    Should be read / written to by the Layers,
    """

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
    A layer is a step in the generation code

    DEPENDS_ON should be a list of other layer names this layer depends on,
    currently not used, but later for parallel world gen (You see that the generation function itself is async)
    """

    TYPE = "minecraft:world_generation_layer"

    NAME = "minecraft:unknown_layer"

    DEPENDS_ON = []

    @staticmethod
    def normalize_config(config: LayerConfig):
        pass

    @staticmethod
    async def add_generate_functions_to_chunk(config: LayerConfig, reference):
        raise NotImplementedError()
