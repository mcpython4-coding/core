"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.event.Registry
import mcpython.common.world.AbstractInterface


class LayerConfig:
    def __init__(self, *config, **cconfig):
        self.config = config
        self.layer: typing.Optional["ILayer"] = None
        for key in cconfig.keys():
            setattr(self, key, cconfig[key])
        self.dimension: typing.Optional[
            mcpython.common.world.AbstractInterface.IDimension
        ] = None


class ILayer(mcpython.common.event.Registry.Registry):
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
