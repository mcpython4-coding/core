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
from abc import ABCMeta, abstractmethod

import mcpython.common.data.serializer.tags.ITagTarget


class AbstractRegistry(metaclass=ABCMeta):
    def __init__(self):
        self.locked = False
        self.phase = None

    @abstractmethod
    def is_valid(self, obj):
        pass

    @abstractmethod
    def register(self, obj, overwrite_existing=False):
        """
        Registers an obj to this registry

        When locked, a RuntimeError is raised
        When an object with the name exists, and overwrite_existing is False, a RuntimeError is raised
        When the object does not extend IRegistryContent, a ValueError is raised
        When the object NAME-attribute is not set, a ValueError is raised
        """
        pass

    @abstractmethod
    def entries_iterator(self):
        pass

    @abstractmethod
    def elements_iterator(self):
        pass

    @abstractmethod
    def lock(self):
        pass

    @abstractmethod
    def unlock(self):
        pass

    @abstractmethod
    def is_valid_key(self, key):
        pass

    @abstractmethod
    def get(self, key, default):
        pass


class IRegistryContent(mcpython.common.data.serializer.tags.ITagTarget.ITagTarget):
    NAME = "minecraft:unknown_registry_content"
    TYPE = "minecraft:unknown_registry_content_type"

    @classmethod
    def on_register(cls, registry):
        pass

    INFO = None  # can be used to display any special info in e.g. /registryinfo-command

    # returns some information about the class stored in registry. used in saves to determine if registry was changed,
    # so could also include an version. Must be pickle-able
    @classmethod
    def compressed_info(cls):
        return cls.NAME
