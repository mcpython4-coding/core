"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.event.Registry
from mcpython import shared as G


class InvalidSaveException(Exception):
    pass


class MissingSaveException(Exception):
    pass


class IDataSerializer(mcpython.common.event.Registry.IRegistryContent):
    """
    Serializer class for any stuff saved in the game files.
    Used for accessing the data and loading it into an way that the game can understand it.
    """

    TYPE = "minecraft:data_serializer"
    PART = None  # which part it can serialize

    @classmethod
    def load(cls, savefile, **kwargs):
        """
        Loads stuff into the game
        :param savefile: the SaveFile object to use
        :param kwargs: the configuration
        """
        raise NotImplementedError()

    @classmethod
    def save(cls, data, savefile, **kwargs):
        """
        Saves data into the storage file
        :param data: the data to save
        :param savefile: the SaveFile object to save
        :param kwargs: the configuration
        """
        raise NotImplementedError()

    @classmethod
    def apply_part_fixer(cls, savefile, fixer):
        """
        Handler function for applying PartFixer instances into the given system
        :param savefile: the SaveFile used
        :param fixer: the fixer instance
        """


dataserializerregistry = mcpython.common.event.Registry.Registry(
    "dataserializer", ["minecraft:data_serializer"]
)


@G.modloader("minecraft", "stage:serializer:parts")
def load():
    from mcpython.server.storage.serializer import (
        General,
        PlayerData,
        Inventory,
        Chunk,
        GameRule,
        RegistryInfo,
    )
