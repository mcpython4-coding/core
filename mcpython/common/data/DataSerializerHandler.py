import typing
from abc import ABC

import mcpython.common.mod.ResourcePipe
import mcpython.ResourceLoader
from mcpython import logger
import mcpython.common.event.EventHandler


class ISerializeAble(ABC):
    SERIALIZER: typing.Type["ISerializer"] = None

    @classmethod
    def deserialize(cls, data: bytes) -> "ISerializeAble":
        return cls.SERIALIZER.deserialize(data)

    def serialize(self) -> bytes:
        return self.SERIALIZER.serialize(self)


class ISerializer:
    @classmethod
    def check(cls, data: bytes) -> bool:
        return True

    @classmethod
    def deserialize(cls, data: bytes) -> ISerializeAble:
        raise NotImplementedError()

    @classmethod
    def serialize(cls, obj: ISerializeAble) -> bytes:
        raise NotImplementedError()


class DatapackSerializationHelper:
    def __init__(self, name: str, path_group: str):
        self.name = name
        self.path_group = path_group
        mcpython.common.mod.ResourcePipe.handler.register_mapper(self.map_pack)
        self.serializer: typing.List[typing.Type[ISerializer]] = []
        self.on_deserialize = None
        self.on_clear = None
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("data:reload:work", self.clear)

    def register_serializer(self, serializer: typing.Type[ISerializer]):
        self.serializer.append(serializer)
        return self

    def map_pack(self, modname: str, pathname: str):
        directory = self.path_group.format(modname=modname, pathname=pathname)
        for file in mcpython.ResourceLoader.get_all_entries(directory):
            if file.endswith("/"): continue

            data = mcpython.ResourceLoader.read_raw(file)

            for serializer in self.serializer:
                if serializer.check(data):
                    obj = serializer.deserialize(data)
                    if callable(self.on_deserialize):
                        self.on_deserialize(obj)
                    break
            else:
                logger.println(
                    "[RESOURCE LOOKUP][{}][WARN] could not read file {} as no valid decoder was found!".format(
                        self.name, file))

    def clear(self):
        if callable(self.on_clear):
            self.on_clear()

