import typing
from abc import ABC

import mcpython.client.state.State
import mcpython.server.worldgen.mode.IWorldGenConfig


class AbstractModeConfig:
    """
    Base class for a world generation mode config
    Serialize-able to save files
    """

    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError()

    def get_mode_instance(self) -> typing.Union[
        typing.Type[mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig],
        mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig
    ]:
        """
        Helper function for creating an instance of a custom world gen config instance specific for this
        configuration.
        """
        raise NotImplementedError()

    def serialize(self):
        raise NotImplementedError()


class AbstractState(mcpython.client.state.State.State, ABC):
    """
    Base class for a configuration screen for a world generator mode
    todo: add sub-class with factory system
        -> data driven creation?
    """

    def get_config_instance(self) -> AbstractModeConfig:
        raise NotImplementedError()

