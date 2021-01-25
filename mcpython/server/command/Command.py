"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import enum
import typing

import mcpython.common.event.Registry


class ParseType(enum.Enum):
    """
    An enum for command entries
    """

    # A defined string like the string "as", without "
    DEFINED_STRING = 0

    # An int. May be negative; cannot be NaN or inf
    INT = 1

    # A string in "" or '', not mixed. May have spaces in it
    STRING = 2

    # A float number, can be negative; must be parse-able by float(), cannot contain spaces
    # Represents a java double
    FLOAT = 3

    # A name for a block. Can start with or without mod namespace; must be lookup-able in the block registry
    BLOCK_NAME = 4

    # A name for an item. Can start with or without mod namespace; must be lookup-able in the item registry
    ITEM_NAME = 5

    # A entity selector; defined by its own registry
    SELECTOR = 6

    # A position. May be selector for position; Selector must be unique
    POSITION = 7

    # A selection of different strings out of an list
    SELECT_DEFINED_STRING = 8

    # A variable list of strings
    OPEN_END_UNDEFINED_STRING = 9

    # A variable string without the ""
    STRING_WITHOUT_QUOTES = 10

    # A boolean value
    BOOLEAN = 11

    def add_subcommand(self, subcommand):
        return SubCommand(self).add_subcommand(subcommand)

    def set_mode(self, parse_mode: "ParseMode"):
        return SubCommand(self, parse_mode)


class ParseMode(enum.Enum):
    """
    An enum for how ParseType-entries are handled
    """

    USER_NEED_ENTER = 0  # user must enter this entry
    OPTIONAL = 1  # user can enter this, but all sub-elements are than invalid
    # todo: add something like OPTIONAL_ALLOW_FURTHER


class SubCommand:
    """
    Class for an part of an command. contains one parse-able entry, one ParseMode and an list of sub-commands
    """

    def __init__(self, entry_type: ParseType, *args, mode=ParseMode.USER_NEED_ENTER, **kwargs):
        """
        Creates an new subcommand
        :param entry_type: the type to use
        :param args: arguments to use for check & parsing
        :param mode: the mode to use
        :param kwargs: optional arguments for check & parsing
        """
        self.type = entry_type
        self.mode = mode
        self.sub_commands: typing.List["SubCommand"] = []
        self.args = args
        self.kwargs = kwargs

    def add_subcommand(self, subcommand: typing.Union["SubCommand", ParseType]):
        """
        Add an new SubCommand to this SubCommand
        :param subcommand: the SubCommand to add
        :return: itself
        """
        if isinstance(subcommand, ParseType):
            subcommand = SubCommand(subcommand)

        self.sub_commands.append(subcommand)
        return self


class ParseBridge:
    """
    A build system for commands
    Inspired by minecraft's brigadier (https://github.com/Mojang/brigadier)

    todo: every SubCommand should have an onParsingEndHere method executing the command instead of
        a single function giving the tree
    """

    def __init__(self, command):
        """
        creates an new ParseBridge
        :param command: the command base class to use
        """
        self.main_entry = None
        self.sub_commands = []
        command.insert_parse_bridge(self)

    def add_subcommand(self, subcommand: typing.Union[SubCommand, ParseType]):
        """
        add an new subcommand to this
        :param subcommand: the subcommand to add or an ParseType
        :return: the object invoked on (the self)
        """
        if isinstance(subcommand, ParseType):
            subcommand = SubCommand(subcommand)
        self.sub_commands.append(subcommand)
        return self


class Command(mcpython.common.event.Registry.IRegistryContent):
    """
    Base class for every command
    """

    TYPE = "minecraft:command"  # the type definition for the registry

    @staticmethod
    def insert_parse_bridge(parse_bridge: ParseBridge):
        """
        Takes an ParseBridge and fills it with life
        :param parse_bridge: the parse bridge to use
        """
        raise NotImplementedError()

    @staticmethod
    def parse(values: list, modes: list, info):
        """
        Parses the command
        :param values: the values parsed over parse bridge
        :param modes: the modes used (a list of decisions)
        :param info: a ParsingCommandInfo for parsing this command
        """

    @staticmethod
    def get_help() -> list:
        """
        :return: help pages for this command. a "<command build>: <description>"-list
        todo: make translate-able
        """
        return []
