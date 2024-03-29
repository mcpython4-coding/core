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
import mcpython.common.event.api
import mcpython.common.event.Registry
from mcpython import shared


class InvalidSaveException(Exception):
    pass


class MissingSaveException(Exception):
    pass


class IDataSerializer(mcpython.common.event.api.IRegistryContent):
    """
    Serializer class for any stuff saved in the game files.
    Used for accessing the data and loading it into an way that the game can understand it.
    """

    TYPE = "minecraft:data_serializer"
    PART = None  # which part it can serialize

    @classmethod
    async def load(cls, save_file, *args, **kwargs):
        """
        Loads stuff into the game
        :param save_file: the SaveFile object to use
        """
        raise NotImplementedError()

    @classmethod
    async def save(cls, data, save_file, *args, **kwargs):
        """
        Saves data into the storage file
        :param data: the data to save
        :param save_file: the SaveFile object to save
        """
        raise NotImplementedError()


data_serializer_registry = mcpython.common.event.Registry.Registry(
    "minecraft:data_serializer", ["minecraft:data_serializer"], "stage:serializer:parts"
)


@shared.mod_loader("minecraft", "stage:serializer:parts")
async def load():
    from mcpython.common.world.serializer import (
        Chunk,
        GameRule,
        General,
        Inventory,
        PlayerData,
        RegistryInfo,
    )
