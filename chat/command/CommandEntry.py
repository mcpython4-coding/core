"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from chat.command.Command import ParseType


class CommandEntry:
    ENTRY_NAME = None

    @staticmethod
    def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
        return start+1, None

    @staticmethod
    def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
        raise NotImplementedError()


def load():
    @G.commandhandler
    class DefiniteString(CommandEntry):
        ENTRY_NAME = ParseType.DEFINIED_STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple: return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool: return entrylist[start] == arguments[0]

    @G.commandhandler
    class IntEntry(CommandEntry):
        ENTRY_NAME = ParseType.INT

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple: return start + 1, int(entrylist[start])

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            try:
                int(entrylist[start])
                return True
            except:
                return False

    @G.commandhandler
    class StringEntry(CommandEntry):
        ENTRY_NAME = ParseType.STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            startc = entrylist[start][0]
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
            startc = entrylist[start][0]
            if startc in "'\"":
                entrys = [entrylist[start]]
                i = 0
                while not entrylist[start + i].endswith(startc):
                    start += 1
                    entrys.append(entrylist[start + i])
                    if start >= len(entrylist):
                        return False
                return True

    @G.commandhandler
    class FloatEntry(CommandEntry):
        ENTRY_NAME = ParseType.FLOAT

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple: return start + 1, float(entrylist[start])

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            try:
                float(entrylist[start])
                return True
            except:
                return False
            
    @G.commandhandler
    class BlockNameEntry(CommandEntry):
        ENTRY_NAME = ParseType.BLOCKNAME

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            return entrylist[start] in G.blockhandler.blocks
        
    @G.commandhandler
    class ItemNameEntry(CommandEntry):
        ENTRY_NAME = ParseType.ITEMNAME

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            return entrylist[start] in G.itemhandler.items
        
    @G.commandhandler
    class SelectorEntry(CommandEntry):
        ENTRY_NAME = ParseType.SELECTOR

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            entry = entrylist[start]
            for selector in G.commandhandler.selectors:
                if selector.is_valid(entry):
                    return start + 1, selector.parse(entry, info) 

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            entry = entrylist[start]
            return any([x.is_valid(entry) for x in G.commandhandler.selectors])
        
    @G.commandhandler
    class PositionEntry(CommandEntry):
        ENTRY_NAME = ParseType.POSITION

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
            
    @G.commandhandler
    class SelectDefinitedString(CommandEntry):
        ENTRY_NAME = ParseType.SELECT_DEFINITED_STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            return start + 1, entrylist[start]

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            return entrylist[start] in arguments
        
    @G.commandhandler
    class OpenEndUndefinitedString(CommandEntry):
        ENTRY_NAME = ParseType.OPEN_END_UNDEFINITED_STRING

        @staticmethod
        def parse(entrylist: list, start: int, info, arguments, kwargs) -> tuple:
            end = start + (kwargs["max"] if "max" in kwargs else len(entrylist))
            return len(entrylist) - 1, (entrylist[start:] if len(entrylist) < end else entrylist[start:end])

        @staticmethod
        def is_valid(entrylist: list, start: int, arguments, kwargs) -> bool:
            return (kwargs["min"] if "min" in kwargs else 0) <= len(entrylist) - start + 1

