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
from abc import ABC

import mcpython.client.state.AbstractState
import mcpython.server.worldgen.mode.IWorldGenConfig


class AbstractModeConfig:
    """
    Base class for a world generation mode config
    Serialize-able to save files
    """

    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError()

    def get_mode_instance(
        self,
    ) -> typing.Union[
        typing.Type[mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig],
        mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig,
    ]:
        """
        Helper function for creating an instance of a custom world gen config instance specific for this
        configuration.
        """
        raise NotImplementedError()

    def serialize(self):
        raise NotImplementedError()


class AbstractConfigState(mcpython.client.state.AbstractState.AbstractState, ABC):
    """
    Base class for a configuration screen for a world generator mode
    todo: add sub-class with factory system
        -> data driven creation?
    """

    def get_config_instance(self) -> AbstractModeConfig:
        raise NotImplementedError()
