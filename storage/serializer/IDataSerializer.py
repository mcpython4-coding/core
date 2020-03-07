import event.Registry
import mod.ModMcpython


class InvalidSaveException(Exception): pass


class IDataSerializer(event.Registry.IRegistryContent):
    TYPE = "minecraft:data_serializer"
    PART = None  # which part it can serialize

    @classmethod
    def load(cls, savefile, **kwargs):
        raise NotImplementedError()

    @classmethod
    def save(cls, data, savefile, **kwargs):
        raise NotImplementedError()


dataserializerregistry = event.Registry.Registry("dataserializer", ["minecraft:data_serializer"])


def load():
    from storage.serializer import (General, PlayerData, Inventory, Chunk, GameRule)


mod.ModMcpython.mcpython.eventbus.subscribe("stage:serializer:parts", load)

