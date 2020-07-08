"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.event.Registry
import mcpython.mod.ModMcpython


class InvalidSaveException(Exception): pass


class MissingSaveException(Exception): pass


class IDataSerializer(mcpython.event.Registry.IRegistryContent):
    TYPE = "minecraft:data_serializer"
    PART = None  # which part it can serialize

    @classmethod
    def load(cls, savefile, **kwargs):
        raise NotImplementedError()

    @classmethod
    def save(cls, data, savefile, **kwargs):
        raise NotImplementedError()

    @classmethod
    def apply_part_fixer(cls, savefile, fixer):
        pass


dataserializerregistry = mcpython.event.Registry.Registry("dataserializer", ["minecraft:data_serializer"])


def load():
    from mcpython.storage.serializer import (General, PlayerData, Inventory, Chunk, GameRule, RegistryInfo)


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:serializer:parts", load)

