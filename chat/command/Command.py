"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import enum


class ParseType(enum.Enum):
    DEFINIED_STRING = 0
    INT = 1
    STRING = 2
    FLOAT = 3
    BLOCKNAME = 4
    ITEMNAME = 5
    PLAYERINVENTORYPART = 6
    SELECTOR = 7
    POSITION = 8
    SELECT_DEFINITED_STRING = 9
    OPEN_END_UNDEFINITED_STRING = 10


class ParseMode(enum.Enum):
    USER_NEED_ENTER = 0
    OPTIONAL = 1


class SubCommand:
    def __init__(self, type, *args, mode=ParseMode.USER_NEED_ENTER, **kwargs):
        self.type = type
        self.mode = mode
        self.sub_commands = []
        self.args = args
        self.kwargs = kwargs

    def add_subcommand(self, subcommand):
        self.sub_commands.append(subcommand)
        return self

    def is_valid(self, entrylist: list, start: int) -> bool:
        entry: str = entrylist[start]
        if self.type == ParseType.DEFINIED_STRING:
            return entry == self.args[0]
        if self.type == ParseType.INT:
            try:
                int(entry)
                return True
            except ValueError:
                return False
        if self.type == ParseType.STRING:
            startc = entry[0]
            if startc in "'\"":
                entrys = [entry]
                i = 0
                while not entrylist[start + i].endswith(startc):
                    start += 1
                    entrys.append(entrylist[start + i])
                    if start >= len(entrylist):
                        return False
                return True
        if self.type == ParseType.FLOAT:
            try:
                float(entry)
                return True
            except ValueError:
                return False
        if self.type == ParseType.BLOCKNAME:
            return entry in G.blockhandler.blocks
        if self.type == ParseType.ITEMNAME:
            return entry in G.itemhandler.items
        if self.type == ParseType.PLAYERINVENTORYPART:
            return entry in G.player.inventorys
        if self.type == ParseType.SELECTOR:
            return entry.startswith("@") and entry in ["@p", "@s"]
        if self.type == ParseType.POSITION:
            value1 = entry.startswith("@") and entry in ["@p", "@s"]
            if value1: return True
            try:
                [float(x) for x in entrylist[start:start+3]]
                return True
            except ValueError:
                return False
        if self.type == ParseType.SELECT_DEFINITED_STRING:
            return entry in self.args or (type(self.args[0]) in (tuple, list, set) and entry in self.args[0])
        if self.type == ParseType.OPEN_END_UNDEFINITED_STRING:
            return (self.kwargs["min"] if "min" in self.kwargs else 0) <= len(entrylist) - start + 1

    def parse(self, entrylist: list, start: int, info) -> tuple:
        """
        parse an value to an result, executed when an command was entered
        :param entrylist: the list to enter
        :param start: the start index
        :return: an index, value object
        """
        entry: str = entrylist[start]
        if self.type in [ParseType.DEFINIED_STRING, ParseType.SELECT_DEFINITED_STRING]:
            return start+1, entry
        if self.type == ParseType.INT:
            return start+1, int(entry)
        if self.type == ParseType.STRING:
            startc = entry[0]
            if startc in "'\"":
                entrys = [entry]
                i = 0
                while not entrylist[start + i].endswith(startc):
                    start += 1
                    entrys.append(entrylist[start + i])
                data = " ".join(entrys)
                if data[0] in "'\"":
                    data = data[1:-1]
                return start+i+1, data
        if self.type == ParseType.FLOAT:
            return start+1, float(entry)
        if self.type == ParseType.BLOCKNAME:
            return start+1, entry
        if self.type == ParseType.ITEMNAME:
            return start+1, entry
        if self.type == ParseType.PLAYERINVENTORYPART:
            return start+1, entry
        if self.type == ParseType.SELECTOR:
            return start+1, [G.player]
        if self.type == ParseType.POSITION:
            value1 = entry.startswith("@") and entry in ["@p", "@s"]
            if value1: return start+1, [G.window.position]
            return start+3, [[float(x) if x != "~" else info.position[i] for i, x in
                              enumerate(entrylist[start:start+3])]]
        if self.type == ParseType.OPEN_END_UNDEFINITED_STRING:
            end = start + (self.kwargs["max"] if "max" in self.kwargs else len(entrylist))
            return len(entrylist) - 1, (entrylist[start:] if len(entrylist) < end else entrylist[start:end])


class ParseBridge:
    def __init__(self, command):
        self.main_entry = None
        self.sub_commands = []
        command.insert_parse_bridge(self)

    def add_subcommand(self, subcommand):
        self.sub_commands.append(subcommand)
        return self


class Command:
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        pass

    @staticmethod
    def parse(values: list, modes: list, info):
        pass

    # a (commandprefix, info)-list
    @staticmethod
    def get_help() -> list:
        return []
