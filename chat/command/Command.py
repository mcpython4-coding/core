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
    SELECTOR = 6
    POSITION = 7
    SELECT_DEFINITED_STRING = 8
    OPEN_END_UNDEFINITED_STRING = 9


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

