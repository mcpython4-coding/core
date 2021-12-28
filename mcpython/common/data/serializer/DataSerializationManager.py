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
import re
import typing

import mcpython.common.data.abstract
import mcpython.common.data.ResourcePipe
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
from mcpython import shared
from mcpython.engine import ResourceLoader, logger

from .abstract import ISerializeAble, ISerializer


class DataSerializationService(
    mcpython.common.data.abstract.AbstractFileWalkingReloadListenerInstanceBased
):
    """
    Special system for wrapping ISerializer's around ReloadListener's
    """

    def __init__(
        self,
        name: str,
        path_group: typing.Union[str, re.Pattern],
        data_deserializer=None,
        data_serializer=None,
        re_run_on_reload=False,
        on_bake=None,
        on_dedicated_server=True,
    ):
        """
        Constructor of the Service
        :param name: the name of the serializer
        :param path_group: the path group to use, as a Pattern-able or a re.Pattern
        :param data_deserializer: a data deserializer taking binary data and outputting some cool stuff for later use
        :param data_serializer: the other way round
        :param re_run_on_reload: re-load stuff when not on first load?
        :param on_bake:
        :param on_dedicated_server: run on dedicated server
        """
        super().__init__()
        self.name = self.NAME = name
        self.PATTERN = (
            re.compile(path_group)
            if not isinstance(path_group, re.Pattern)
            else path_group
        )

        self.path_group = path_group
        self.serializer: typing.List[typing.Type[ISerializer]] = []
        self.on_deserialize = None
        self.on_unload = None
        self.data_deserializer = data_deserializer
        self.data_serializer = data_serializer
        self.re_run_on_reload = re_run_on_reload
        self.on_bake = on_bake if on_bake is not None else lambda: None
        self.on_dedicated_server = on_dedicated_server

    def register_listener(self):
        if self.on_dedicated_server or shared.IS_CLIENT:
            mcpython.common.data.ResourcePipe.handler.register_listener(self)

    def register_serializer(self, serializer: typing.Type[ISerializer]):
        logger.println(
            f"[SERIALIZER][INFO] got serializer of wrapper {self.NAME}: {serializer}"
        )

        self.serializer.append(serializer)
        return self

    async def on_reload(self, is_first_load=False):
        if not (is_first_load or self.re_run_on_reload):
            return

        await super().on_reload(is_first_load)

    async def load_file(self, file: str, is_first_load=False):
        try:
            data = await mcpython.engine.ResourceLoader.read_raw(file)

            if callable(self.data_deserializer):
                data = await self.data_deserializer(data)

            for serializer in self.serializer:
                if await serializer.check(data):
                    obj = await serializer.deserialize(data)

                    if callable(self.on_deserialize):
                        await self.on_deserialize(obj)

                    break

            else:
                logger.println(
                    "[RESOURCE LOOKUP][{}][WARN] could not read file '{}' as no valid decoder was found!".format(
                        self.name, file
                    )
                )
        except:
            logger.print_exception(
                "during deserializing '{}' with handler {}; skipping...".format(
                    file, self.name
                )
            )

    def on_unload(self):
        if callable(self.on_unload):
            self.on_unload()
