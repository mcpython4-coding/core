"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import enum

import mcpython.common.event.Registry


class ParseType(enum.Enum):
    """
    An enum for command entrys
    """
    DEFINIED_STRING = 0  # a definied string like "as"
    INT = 1  # an int. may be negative
    STRING = 2  # an string in "" or ''. not mixed. may have spaces in it
    FLOAT = 3  # an float number, can be negative
    BLOCKNAME = 4  # an name for an block. can start with or without mod prefix
    ITEMNAME = 5  # an name for an item. can start with or without mod prefix
    SELECTOR = 6  # an entity selector
    POSITION = 7  # an position. may be selector
    SELECT_DEFINITED_STRING = 8  # an selection of diffrent strings out of an list
    OPEN_END_UNDEFINITED_STRING = 9  # an variable list of strings
    STRING_WITHOUT_QUOTES = 10  # an varialbe string without the ""
    BOOLEAN = 11  # an boolean value

    def add_subcommand(self, subcommand):
        return SubCommand(self).add_subcommand(subcommand)

    def set_mode(self, parsemode):
        return SubCommand(self, parsemode)


class ParseMode(enum.Enum):
    """
    An enum for how ParseType-entries are handled
    """

    USER_NEED_ENTER = 0  # user must enter this entry
    OPTIONAL = 1  # user can enter this, but all sub-elements are than invalid
    # todo: add something like OPTIONAL_ALLOW_FURTHER


class SubCommand:
    """
    class for an part of an command. contains one parse-able entry, one ParseMode and an list of sub-commands
    """

    def __init__(self, type, *args, mode=ParseMode.USER_NEED_ENTER, **kwargs):
        """
        creates an new subcommand
        :param type: the type to use
        :param args: arguments to use for check & parsing
        :param mode: the mode to use
        :param kwargs: optional arguments for check & parsing
        """
        self.type = type
        self.mode = mode
        self.sub_commands = []
        self.args = args
        self.kwargs = kwargs

    def add_subcommand(self, subcommand):
        """
        add an new SubCommand to this SubCommand
        :param subcommand: the SubCommand to add
        :return: itself
        """
        self.sub_commands.append(subcommand)
        return self


class ParseBridge:
    """
    An build system for commands
    """

    def __init__(self, command):
        """
        creates an new ParseBridge
        :param command: the command base class to use
        """
        self.main_entry = None
        self.sub_commands = []
        command.insert_parse_bridge(self)

    def add_subcommand(self, subcommand):
        """
        add an new subcommand to this
        :param subcommand: the subcommand to add or an ParseType
        :return: the object invoked on (the self)
        """
        if type(subcommand) == ParseType: subcommand = SubCommand(subcommand)
        self.sub_commands.append(subcommand)
        return self


class Command(mcpython.common.event.Registry.IRegistryContent):
    """
    base class for every command
    """

    TYPE = "minecraft:command"  # the type defintion for the registry

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        """
        takes an ParseBridge and fills it with life
        :param parsebridge: the parsebridge to use
        """
        raise NotImplementedError()

    @staticmethod
    def parse(values: list, modes: list, info):
        """
        parse the command
        :param values: the values parsed over parsebridge
        :param modes: the modes used (an list of decicions)
        :param info: an ParsingCommandInfo for parsing this command
        """

    @staticmethod
    def get_help() -> list:
        """
        :return: help pages for this command. a "<command build>: <description>"-list
        todo: make translated
        """
        return []

