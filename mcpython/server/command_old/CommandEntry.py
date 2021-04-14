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
from mcpython import shared, logger
import mcpython.common.event.Registry
from mcpython.server.command.Command import CommandArgumentType
import math


class CommandEntry(mcpython.common.event.Registry.IRegistryContent):
    """
    A parse-able command entry
    """

    TYPE = "minecraft:command_entry"

    @staticmethod
    def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
        """
        parse an entry in entry list to an value
        :param entry_list: the entries to parse
        :param start: which entry to start at
        :param info: the command info to use
        :param arguments: handed over creation arguments
        :param kwargs: handed over optional creative arguments
        :return: an (new start, value)-tuple
        """
        return start + 1, None

    @staticmethod
    def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
        """
        checks if entry is valid
        :param entry_list: the entries to check
        :param start: which entry to start at
        :param arguments: handed over creation arguments
        :param kwargs: handed over optional creation arguments
        :return: if entry is valid, as a bool
        """
        raise NotImplementedError()


def load():

    @shared.registry
    class StringEntry(CommandEntry):
        """
        String entry
        """

        NAME = CommandArgumentType.STRING

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            start_char = entry_list[start][0]  # with what does it start?
            if start_char in "'\"":
                entries = [entry_list[start]]
                i = 0
                while not entry_list[start + i].endswith(start_char):
                    start += 1
                    entries.append(entry_list[start + i])

                data = " ".join(entries)
                if data[0] in "'\"":
                    data = data[1:-1]

                return start + i + 1, data

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            start_char = entry_list[start][0]  # with what does it start?
            if start_char in "'\"":
                entries = [entry_list[start]]
                i = 0
                while not entry_list[start + i].endswith(start_char):
                    start += 1
                    entries.append(entry_list[start + i])
                    if start >= len(entry_list):

                        return False  # it does NOT close

                return True  # it does close

            return False  # it does NOT start

    @shared.registry
    class StringWithoutQuotesEntry(CommandEntry):
        """
        string entry
        """

        NAME = CommandArgumentType.STRING_WITHOUT_QUOTES

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            return True

    @shared.registry
    class FloatEntry(CommandEntry):
        """
        float entry
        """

        NAME = CommandArgumentType.FLOAT

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, float(entry_list[start])

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            try:
                float(entry_list[start])  # try to convert to float
                return True
            except ValueError:
                return False

    @shared.registry
    class DimensionNameEntry(CommandEntry):
        """
        Dimension name entry
        """

        NAME = CommandArgumentType.DIMENSION_NAME

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            # is this item arrival?
            flag = entry_list[start] in shared.world.get_dimension_names()

            if not flag:
                logger.println("[INFORM] invalid due to missing dimension")

            return flag

    @shared.registry
    class SelectorEntry(CommandEntry):
        """
        Selector entry
        """

        NAME = CommandArgumentType.SELECTOR

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            entry = entry_list[start]
            for selector in shared.registry.get_by_name("minecraft:command").selector:
                if selector.is_valid(
                    entry
                ):  # is this the selector we are searching for?
                    return start + 1, selector.parse(entry, info)

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            entry = entry_list[start]

            # have we any valid selector?
            return any(
                [
                    x.is_valid(entry)
                    for x in shared.registry.get_by_name("minecraft:command").selector
                ]
            )

    @shared.registry
    class OpenEndUndefinedStringEntry(CommandEntry):
        """
        open end undefined string entry
        """

        NAME = CommandArgumentType.OPEN_END_UNDEFINED_STRING

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            end = start + (kwargs["max"] if "max" in kwargs else len(entry_list))
            return len(entry_list) - 1, (
                entry_list[start:] if len(entry_list) < end else entry_list[start:end]
            )

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            return (kwargs["min"] if "min" in kwargs else 0) <= len(
                entry_list
            ) - start + 1  # if length is in range

    @shared.registry
    class BooleanEntry(CommandEntry):
        TABLE = [("true", "True"), ("false", "False")]

        NAME = CommandArgumentType.BOOLEAN

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start] in BooleanEntry.TABLE[0]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            return any([entry_list[start] in array for array in BooleanEntry.TABLE])
