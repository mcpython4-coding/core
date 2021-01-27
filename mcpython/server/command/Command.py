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
import itertools

import mcpython.common.event.Registry


class CommandArgumentType(enum.Enum):
    """
    An enum for command entries
    """

    # A defined string like the string "as", without "
    DEFINED_STRING = enum.auto()

    # An int. May be negative; cannot be NaN or inf
    # todo: add a non-negative variant
    # todo: add variant with NaN and inf
    INT = enum.auto()

    # A string in "" or '', not mixed. May have spaces in it, determined by the " or ' s
    STRING = enum.auto()

    # A float number, can be negative; must be parse-able by float(), cannot contain spaces
    # Represents a java double
    # todo: add a non-negative variant
    FLOAT = enum.auto()

    # A name for a block. Can start with or without mod namespace; must be lookup-able in the block registry
    # todo: add variant with forced namespace
    BLOCK_NAME = enum.auto()

    # A name for an item. Can start with or without mod namespace; must be lookup-able in the item registry
    # todo: add variant with forced namespace
    ITEM_NAME = enum.auto()

    # todo: add entity name

    # A name of a dimension in the active world
    DIMENSION_NAME = enum.auto()

    # A entity selector; defined by its own registry
    SELECTOR = enum.auto()

    # A position. May be selector; Selector must point to exactly one entity
    # todo: add variant only for whole blocks
    POSITION = enum.auto()

    # A selection of different strings out of an list
    SELECT_DEFINED_STRING = enum.auto()

    # A variable list of strings
    OPEN_END_UNDEFINED_STRING = enum.auto()

    # A variable string without the "", without spaces
    STRING_WITHOUT_QUOTES = enum.auto()

    # A boolean value
    BOOLEAN = enum.auto()

    def add_node(self, subcommand):
        return Node(self).add_node(subcommand)

    def set_mode(self, parse_mode: "CommandArgumentMode"):
        return Node(self, parse_mode)


class CommandArgumentMode(enum.Enum):
    """
    An enum for how ParseType-entries are handled
    todo: merge as optional: bool = False into node creation
    """

    USER_NEED_ENTER = 0  # user must enter this entry
    OPTIONAL = 1  # user can enter this, but all sub-elements are than invalid


class Node:
    """
    Class for an part of a command (a "Node"). Contains one parse-able entry, one ParseMode and a list of sub-commands
    todo: add variant without entry only linking a subset of nodes
    """

    def __init__(
        self,
        entry_type: CommandArgumentType,
        *args,
        mode=CommandArgumentMode.USER_NEED_ENTER,
        on_node_iterated: typing.Callable[
            [typing.Any, typing.List, typing.List], None
        ] = None,
        on_node_executed: typing.Callable[
            [typing.Any, typing.List, typing.List], None
        ] = None,
        **kwargs
    ):
        """
        Creates a new Node instance, representing
        :param entry_type: the type to use
        :param args: arguments to use for check & parsing
        :param mode: the mode to use
        :param kwargs: optional arguments for check & parsing
        :param on_node_executed: run when this node is the last one on the stack; signature: (info, values, node stack)
        :param on_node_iterated: run when this node is used during command parsing; signature: (info, values, node stack)
        todo: add attribute if it can be the last on the stack or not
        todo: add permission config entry
        todo: add "optional" parameter
        """
        self.type = entry_type
        self.mode = mode
        self.nodes: typing.List["Node"] = []
        self.args = args
        self.kwargs = kwargs
        self.on_node_executed = on_node_executed
        self.on_node_iterated = on_node_iterated

    def add_node(self, node: typing.Union["Node", CommandArgumentType]):
        """
        Add a new sub-Node to this Node
        :param node: the Node to add
        :return: the current Node
        """
        if isinstance(node, CommandArgumentType):
            node = Node(node)

        self.nodes.append(node)
        return self

    def get_node_ends(self) -> typing.Iterable["Node"]:
        if len(self.nodes) == 0:
            return ((self),)
        if all(node.mode == CommandArgumentMode.OPTIONAL for node in self.nodes):
            yield self
        for node in self.nodes:
            yield from node.get_node_ends()


class CommandSyntaxHolder:
    """
    A build system for commands
    Inspired by minecraft's brigadier (https://github.com/Mojang/brigadier)
    """

    def __init__(self, command: typing.Type["Command"]):
        """
        Creates a new CommandSyntaxHolder instance
        :param command: the command base class to use
        """
        self.main_entry = None
        self.nodes = []
        command.insert_command_syntax_holder(self)

    def add_node(self, node: typing.Union[Node, CommandArgumentType]):
        """
        add a new Node to this
        :param node: the Node to add or a ParseType
        :return: the object invoked on (the self)
        """
        if isinstance(node, CommandArgumentType):
            node = Node(node)

        self.nodes.append(node)
        return self


class Command(mcpython.common.event.Registry.IRegistryContent):
    """
    Base class for every command
    """

    TYPE = "minecraft:command"  # the type definition for the registry

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        """
        Takes a CommandSyntaxHolder and fills it with life
        :param command_syntax_holder: the syntax holder to use
        """
        raise NotImplementedError()

    @staticmethod
    def parse(values: list, modes: list, info):
        """
        Parses the command
        :param values: the values parsed over parse bridge
        :param modes: the modes used (a list of decisions)
        :param info: a ParsingCommandInfo for parsing this command
        todo: remove
        """

    @staticmethod
    def get_help() -> list:
        """
        :return: help pages for this command. a "<command build>: <description>"-list
        todo: make translate-able
        """
        return []
