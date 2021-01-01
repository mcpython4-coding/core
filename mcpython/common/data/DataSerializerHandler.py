"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing
from abc import ABC

import mcpython.common.mod.ResourcePipe
import mcpython.ResourceLoader
from mcpython import logger
import mcpython.common.event.EventHandler
from mcpython import shared


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
    def __init__(
        self,
        name: str,
        path_group: str,
        data_formatter=None,
        data_un_formatter=None,
        re_run_on_reload=False,
        load_on_stage: str = None,
    ):
        self.name = name
        self.path_group = path_group
        self.serializer: typing.List[typing.Type[ISerializer]] = []
        self.on_deserialize = None
        self.on_clear = None
        self.data_formatter = data_formatter
        self.data_un_formatter = data_un_formatter
        self.re_run_on_reload = re_run_on_reload
        self.load_on_stage = load_on_stage

        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "data:reload:work", self.clear
        )

        mcpython.common.mod.ResourcePipe.handler.register_mapper(self.map_pack)

    def register_serializer(self, serializer: typing.Type[ISerializer]):
        self.serializer.append(serializer)
        return self

    def map_pack(self, modname: str, pathname: str):
        directory = self.path_group.format(modname=modname, pathname=pathname)
        for file in mcpython.ResourceLoader.get_all_entries(directory):
            if file.endswith("/"):
                continue

            if self.load_on_stage is None:
                self.load_file(file)
            else:
                shared.mod_loader(modname, self.load_on_stage, file)(
                    self.load_file
                )

    def load_file(self, file: str):
        try:
            data = mcpython.ResourceLoader.read_raw(file)

            if callable(self.data_formatter):
                data = self.data_formatter(data)

            for serializer in self.serializer:
                if serializer.check(data):
                    obj = serializer.deserialize(data)
                    if callable(self.on_deserialize):
                        self.on_deserialize(obj)
                    break
            else:
                logger.println(
                    "[RESOURCE LOOKUP][{}][WARN] could not read file '{}' as no valid decoder was found!".format(
                        self.name, file
                    )
                )
        except:
            logger.print_exception("during deserializing '{}'".format(file))

    def clear(self):
        if callable(self.on_clear):
            self.on_clear()
        if self.re_run_on_reload:
            for modname, pathname in mcpython.common.mod.ResourcePipe.handler.mods:
                self.map_pack(modname, pathname)
