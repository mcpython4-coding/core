"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G, logger
import mcpython.common.event.Registry
from mcpython.client.chat.command.Command import ParseType


class CommandEntry(mcpython.common.event.Registry.IRegistryContent):
    """
    an parseable command entry
    """

    TYPE = "minecraft:command_entry"

    @staticmethod
    def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
        """
        parse an entry in entrylist to an value
        :param entrylist: the entrys to parse
        :param start: which entry to start at
        :param info: the command info to use
        :param arguments: overgiven creation arguments
        :param kwargs: overgiven optional creative arguments
        :return: an (new start, value)-tuple
        """
        return start+1, None

    @staticmethod
    def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
        """
        checks if entry is valid
        :param entrylist: the entrys to check
        :param start: which entry to start at
        :param arguments: overgiven creation arguments
        :param kwargs: overgiven optional creation arguments
        :return: if entry is valid
        """
        raise NotImplementedError()


def load():
    @G.registry
    class DefiniteString(CommandEntry):
        """
        Entry for definite string
        """

        NAME = ParseType.DEFINIED_STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple: return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool: return entrylist[start] == arguments[0]

    @G.registry
    class IntEntry(CommandEntry):
        """
        entry for int
        """

        NAME = ParseType.INT

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple: return start + 1, int(entrylist[start])

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            try:
                int(entrylist[start])  # try to convert to int
                return True
            except:
                return False

    @G.registry
    class StringEntry(CommandEntry):
        """
        string entry
        """

        NAME = ParseType.STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            startc = entrylist[start][0]  # with what does it start?
            if startc in "'\"":
                entrys = [entrylist[start]]
                i = 0
                while not entrylist[start + i].endswith(startc):
                    start += 1
                    entrys.append(entrylist[start + i])
                data = " ".join(entrys)
                if data[0] in "'\"":
                    data = data[1:-1]
                return start + i + 1, data

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            startc = entrylist[start][0]  # with what does it start?
            if startc in "'\"":
                entrys = [entrylist[start]]
                i = 0
                while not entrylist[start + i].endswith(startc):
                    start += 1
                    entrys.append(entrylist[start + i])
                    if start >= len(entrylist):
                        return False  # it does NOT close
                return True  # it does close
            return False  # it does NOT start

    @G.registry
    class StringWithoutQuotesEntry(CommandEntry):
        """
        string entry
        """

        NAME = ParseType.STRING_WITHOUT_QUOTES

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool: return True

    @G.registry
    class FloatEntry(CommandEntry):
        """
        float entry
        """

        NAME = ParseType.FLOAT

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple: return start + 1, float(entrylist[start])

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            try:
                float(entrylist[start])  # try to convert to float
                return True
            except:
                return False
            
    @G.registry
    class BlockNameEntry(CommandEntry):
        """
        blockname entry
        """

        NAME = ParseType.BLOCKNAME

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            flag = entrylist[start] in G.registry.get_by_name("block").full_table or entrylist[start] in ("air", "minecraft:air")  # is this block arrival?
            if not flag:
                logger.println("[INFORM] invalid due to missing registry entry. Use '/registryinfo block' for an list "
                               "of all found blocks!")
            return flag
        
    @G.registry
    class ItemNameEntry(CommandEntry):
        """
        itemname entry
        """

        NAME = ParseType.ITEMNAME

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            flag = entrylist[start] in G.registry.get_by_name("item").registered_object_map  # is this item arrival?
            if not flag:
                logger.println("[INFORM] invalid due to missing registry entry. Use '/registryinfo item' for an list "
                               "of all found blocks")
            return flag
        
    @G.registry
    class SelectorEntry(CommandEntry):
        """
        Selector entry
        """

        NAME = ParseType.SELECTOR

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            entry = entrylist[start]
            for selector in G.registry.get_by_name("command").selector:
                if selector.is_valid(entry):  # is this the selector we are searching for?
                    return start + 1, selector.parse(entry, info) 

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            entry = entrylist[start]
            # have we any valid selector?
            return any([x.is_valid(entry) for x in G.registry.get_by_name("command").selector])
        
    @G.registry
    class PositionEntry(CommandEntry):
        """
        position entry
        """

        NAME = ParseType.POSITION

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            if SelectorEntry.is_valid(entrylist, start, arguments, kwargs):
                return start + 1, SelectorEntry.parse(entrylist, start, info, arguments, kwargs)[0].position
            x, y, z = tuple(entrylist[start:start+3])
            x = PositionEntry._parse_coordinate_to_real(x, 0, info)
            y = PositionEntry._parse_coordinate_to_real(y, 1, info)
            z = PositionEntry._parse_coordinate_to_real(z, 2, info)
            return start + 3, (x, y, z)

        @staticmethod
        def _parse_coordinate_to_real(r: str, index: int, info) -> float:
            """
            parse an coordinate (could be relative) to an valid coordinate
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
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            if SelectorEntry.is_valid(entrylist, start, arguments, kwargs):
                return True
            try:
                [float(x) if not x.startswith("~") else None for x in entrylist[start:start + 3]]
                return True
            except ValueError:
                return False
            
    @G.registry
    class SelectDefinitedStringEntry(CommandEntry):
        """
        select definite string entry
        """

        NAME = ParseType.SELECT_DEFINITED_STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            return entrylist[start] in arguments  # check if should be used

    @G.registry
    class OpenEndUndefinedStringEntry(CommandEntry):
        """
        open end undefined string entry
        """

        NAME = ParseType.OPEN_END_UNDEFINITED_STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            end = start + (kwargs["max"] if "max" in kwargs else len(entrylist))
            return len(entrylist) - 1, (entrylist[start:] if len(entrylist) < end else entrylist[start:end])

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            return (kwargs["min"] if "min" in kwargs else 0) <= len(entrylist) - start + 1  # if length is in range

    @G.registry
    class BooleanEntry(CommandEntry):
        TABLE = [("true", "True"), ("false", "False")]

        NAME = ParseType.BOOLEAN

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start] in BooleanEntry.TABLE[0]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            return any([entrylist[start] in array for array in BooleanEntry.TABLE])


