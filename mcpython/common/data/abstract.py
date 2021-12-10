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
from abc import ABC

from mcpython.engine import ResourceLoader


class AbstractReloadListener(ABC):
    NAME = None
    DEPENDS_ON = set()

    @classmethod
    async def on_reload(cls, is_first_load=False):
        """
        Invoked when it is time to load resources
        :param is_first_load: indicates if this is the first resource load or not
        """
        raise NotImplementedError

    @classmethod
    def on_unload(cls):
        """
        Invoked before a reload, to delete all previous resources or do some fancy stuff with them
        """

    @classmethod
    def on_bake(cls):
        """
        Invoked after most of the stuff is loaded
        """


class AbstractFileWalkingReloadListener(AbstractReloadListener, ABC):
    PATTERN: typing.Optional[re.Pattern] = None
    SPECIAL_WALK = False
    DIRECTORY = ""

    @classmethod
    async def on_reload(cls, is_first_load=False):
        if not cls.SPECIAL_WALK:
            entries = ResourceLoader.get_all_entries(cls.DIRECTORY)
        else:
            entries = ResourceLoader.get_all_entries_special(cls.DIRECTORY)

        for entry in entries:
            if entry.endswith("/"):
                continue
            if cls.PATTERN is None or cls.PATTERN.match(entry):
                cls.load_file(entry, is_first_load=is_first_load)

    @classmethod
    def load_file(cls, file: str, is_first_load=False):
        """
        Similar to on_reload, but it invoked for each matching file
        :param file: the file to load
        :param is_first_load: same as in on_reload
        """
        raise NotImplementedError


class AbstractFileWalkingReloadListenerInstanceBased(AbstractReloadListener, ABC):
    def __init__(self):
        self.PATTERN: typing.Optional[re.Pattern] = None
        self.SPECIAL_WALK = False
        self.DIRECTORY = ""

    async def on_reload(self, is_first_load=False):
        if not self.SPECIAL_WALK:
            entries = ResourceLoader.get_all_entries(self.DIRECTORY)
        else:
            entries = ResourceLoader.get_all_entries_special(self.DIRECTORY)

        for entry in entries:
            if entry.endswith("/"):
                continue

            if self.PATTERN is None or self.PATTERN.match(entry):
                await self.load_file(entry, is_first_load=is_first_load)

    async def load_file(self, file: str, is_first_load=False):
        """
        Similar to on_reload, but it invoked for each matching file
        :param file: the file to load
        :param is_first_load: same as in on_reload
        """
        raise NotImplementedError

    def on_unload(self):
        pass

    def on_bake(self):
        pass
