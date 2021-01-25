"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.common.event.Registry
from mcpython.server.command.Command import ParseType
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
    class DefiniteString(CommandEntry):
        """
        Entry for definite string
        """

        NAME = ParseType.DEFINED_STRING

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            return entry_list[start] == arguments[0]

    @shared.registry
    class IntEntry(CommandEntry):
        """
        Entry for int
        """

        NAME = ParseType.INT

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, int(entry_list[start])

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            try:
                v = int(entry_list[start])  # try to convert to int
                return not (math.isnan(v) or math.isinf(v))
            except ValueError:
                return False

    @shared.registry
    class StringEntry(CommandEntry):
        """
        String entry
        """

        NAME = ParseType.STRING

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

        NAME = ParseType.STRING_WITHOUT_QUOTES

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

        NAME = ParseType.FLOAT

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
    class BlockNameEntry(CommandEntry):
        """
        blockname entry
        """

        NAME = ParseType.BLOCK_NAME

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            # is this block arrival?
            flag = entry_list[start] in shared.registry.get_by_name(
                "minecraft:block"
            ) or entry_list[start] in (
                "air",
                "minecraft:air",
            )

            if not flag:
                logger.println(
                    "[INFORM] invalid due to missing registry entry. Use '/registryinfo block' for an list "
                    "of all found blocks!"
                )

            return flag

    @shared.registry
    class ItemNameEntry(CommandEntry):
        """
        Item name entry
        """

        NAME = ParseType.ITEM_NAME

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            # is this item arrival?
            flag = (
                entry_list[start]
                in shared.registry.get_by_name("minecraft:item")
            )

            if not flag:
                logger.println(
                    "[INFORM] invalid due to missing registry entry. Use '/registryinfo item' for an list "
                    "of all found blocks"
                )

            return flag

    @shared.registry
    class SelectorEntry(CommandEntry):
        """
        Selector entry
        """

        NAME = ParseType.SELECTOR

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
    class PositionEntry(CommandEntry):
        """
        Position entry
        """

        NAME = ParseType.POSITION

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            if SelectorEntry.is_valid(entry_list, start, arguments, kwargs):
                return (
                    start + 1,
                    SelectorEntry.parse(entry_list, start, info, arguments, kwargs)[
                        0
                    ].position,
                )
            x, y, z = tuple(entry_list[start : start + 3])
            x = PositionEntry._parse_coordinate_to_real(x, 0, info)
            y = PositionEntry._parse_coordinate_to_real(y, 1, info)
            z = PositionEntry._parse_coordinate_to_real(z, 2, info)
            return start + 3, (x, y, z)

        @staticmethod
        def _parse_coordinate_to_real(r: str, index: int, info) -> float:
            """
            Parses a coordinate (could be relative) to a valid coordinate
            :param r: the coordinate to use
            :param index: the index in the info position
            :param info: the info to use
            :return: an float value representing this
            """
            if r.startswith("~"):
                v = info.position[index]
                if len(r) > 1:
                    v += int(r[1:])
                return v

            return float(r)

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            if SelectorEntry.is_valid(entry_list, start, arguments, kwargs):
                return True
            try:
                [
                    float(x) if not x.startswith("~") else None
                    for x in entry_list[start : start + 3]
                ]
                return True
            except ValueError:
                return False

    @shared.registry
    class SelectDefinedStringEntry(CommandEntry):
        """
        Select definite string entry
        """

        NAME = ParseType.SELECT_DEFINED_STRING

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            return entry_list[start] in arguments  # check if should be used

    @shared.registry
    class OpenEndUndefinedStringEntry(CommandEntry):
        """
        open end undefined string entry
        """

        NAME = ParseType.OPEN_END_UNDEFINED_STRING

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

        NAME = ParseType.BOOLEAN

        @staticmethod
        def parse(entry_list: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entry_list[start] in BooleanEntry.TABLE[0]

        @staticmethod
        def is_valid(entry_list: list, start: int, arguments, kwargs) -> bool:
            return any([entry_list[start] in array for array in BooleanEntry.TABLE])
