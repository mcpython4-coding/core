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
import random

# This is real cool stuff, a builder for commands, like mojang's bridagier, but a lot more simple
# This is the independent implementation, beside some command entries only making sense here
# Feel free to use in other games, see LICENCE for licence for using the code
import typing
from abc import ABC

from mcpython import logger, shared


class CommandExecutionTracker:
    """
    Helper code for decoding a command
    It is "tracking" were in the command we are, what values we have etc.
    It is part of the two major stages of decoding, being the node selection system and on the other side being
        the actual parsing into values
    """

    @classmethod
    def from_string(cls, string: str) -> "CommandExecutionTracker":
        """
        Splits up the command into parts
        :param string: the string
        todo: do not split when in " or ' or brackets
        """
        return cls(string.split(" "))

    def __init__(self, content: typing.List[str] = None):
        """
        Creates a new tracker
        Use from_string() when working with strings
        :param content: optional, a list of strings as bases
        """

        self.content = content if content is not None else []
        self.collected_values = []

        self.current_index = 0
        self.index_pool = []

        self.parsing_errors = []

    def collect(self, value):
        """
        Adds a value to the parsed value list
        :param value: the value
        """
        self.collected_values.append(value)
        return self

    def rollback(self):
        """
        Rolls back this tracker to the latest saved point; the saved point is deleted
        """
        self.current_index = self.index_pool.pop(-1)
        return self

    def get(self, offset: int = 0) -> str:
        """
        Gets the current part
        :param offset: how many parts to go ahead of current pointer
        :return: the part
        """
        return self.content[self.current_index + offset]

    def get_multi(self, count: int, offset: int = 0) -> typing.List[str]:
        """
        Similar to get(), but will return the next <count> entries
        :param count: the amount of entries to get
        :param offset: the offset from current pointer
        :return: the parts, as a list
        """
        return self.content[
            self.current_index + offset : self.current_index + count + offset
        ]

    def increase(self, count: int):
        """
        Increases the local pointer by <count>
        """
        self.current_index += count
        return self

    def save(self):
        """
        Saves the current state for later rollback()-s
        """
        self.index_pool.append(self.current_index)
        return self

    def has(self, count: int) -> bool:
        """
        Checks if there are at least <count> parts pending
        Use this before calling get() or get_multi()
        """
        return len(self.content) >= self.current_index + count


class ICommandElementIdentifier(ABC):
    """
    An abstract entry in the parsing tree
    Defines validation & parsing of entries
    """

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        """
        Checks if the data at the current tracker pointer is a valid entry here
        :param node: the current node
        :param tracker: the tracker
        :return: if valid or not
        """
        raise NotImplementedError

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        """
        Parses the tracker data
        Does not need to do checks, is_valid() must be called beforehand
        WARNING: if is_valid() return True, the tracker will be saved, and than this method is directly
            invoked, before checking following nodes
        WARNING: do NOT forget to increase tracker pointer by calling increase()
        """
        raise NotImplementedError


class DefinedString(ICommandElementIdentifier):
    """
    Class for a set of defines strings without quotation marks
    Used internally also as the main node of a command
    todo: add a node only containing defined strings -> faster parsing by dict lookup
    """

    def __init__(self, *strings: str):
        assert all(" " not in e for e in strings), (
            "no whitespaces currently allowed in defined strings",
            strings,
        )
        self.strings = strings

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return tracker.has(1) and tracker.get() in self.strings

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        tracker.collect(tracker.get())
        tracker.increase(1)

    def __eq__(self, other):
        return isinstance(other, DefinedString) and self.strings == other.strings


class Int(ICommandElementIdentifier):
    """
    Helper for integers, with auto-parsing and validation
    """

    def __init__(
        self,
        only_positive=False,
        only_negative=False,
        include_zero=True,
        value_range=None,
    ):
        """
        :param only_positive: only positive integers
        :param only_negative: only negative integers
        :param include_zero: zero allowed
        :param value_range: a range of (min, max) for the integer, or None for open range
        """
        self.value_range = value_range
        self.include_zero = include_zero
        self.only_negative = only_negative
        self.only_positive = only_positive

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        v = tracker.get()
        if not v.removeprefix("-").isdigit():
            return False
        if (self.only_positive if v.startswith("-") else self.only_negative) and not (
            v == "0" and self.include_zero
        ):
            return False

        if v == "0" and not self.include_zero:
            return False

        if self.value_range is not None:
            v = int(v)
            return self.value_range[0] <= v <= self.value_range[1]

        return True

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        v = tracker.get()
        tracker.increase(1)
        tracker.collect(int(v))


class IntPosition(ICommandElementIdentifier):
    """
    A position, in int terms
    todo: allow local references
    """

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return tracker.has(3) and all(
            e.removeprefix("-").isdigit() for e in tracker.get_multi(3)
        )

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        p = tracker.get_multi(3)
        tracker.increase(3)
        tracker.collect(tuple(int(e) for e in p))

    def __eq__(self, other):
        return isinstance(other, IntPosition)


class Position(ICommandElementIdentifier):
    """
    A position, in float terms
    todo: allow local references, and selectors
    """

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return tracker.has(3) and all(
            e.removeprefix("-").replace(".", "", 1).isdigit()
            for e in tracker.get_multi(3)
        )

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        p = tracker.get_multi(3)
        tracker.increase(3)
        tracker.collect(lambda env: [tuple(float(e) for e in p)])

    def __eq__(self, other):
        return isinstance(other, IntPosition)


class RegistryContent(ICommandElementIdentifier):
    """
    Registry entry getter
    registry name given, will return the entry of the registry by calling get() on it
    """

    def __init__(self, registry: str):
        self.inner_registry = shared.registry.get_by_name(registry)

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return tracker.has(1) and self.inner_registry.is_valid_key(tracker.get())

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        key = tracker.get()
        tracker.increase(1)
        tracker.collect(self.inner_registry.get(key))

    def __eq__(self, other):
        return (
            isinstance(other, RegistryContent)
            and self.inner_registry == other.inner_registry
        )


class Block(ICommandElementIdentifier):
    """
    Special entry for a block, for adding meta information
    """

    BLOCK_REGISTRY = shared.registry.get_by_name("minecraft:block")

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        if not tracker.has(1):
            return False

        element = tracker.get()
        name = element.split("[")[0]

        return self.BLOCK_REGISTRY.is_valid_key(name)

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        element = tracker.get()
        tracker.increase(1)
        name = element.split("[")[0]
        entry = self.BLOCK_REGISTRY.get(name)()

        if "[" in element:
            logger.println(
                "[COMMAND PARSER][WARN] unimplemented feature found: block with block state"
            )
            # todo: implement

        tracker.collect(entry)

    def __eq__(self, other):
        return isinstance(other, Block)


class Item(ICommandElementIdentifier):
    """
    Special entry for an item, for adding meta information
    """

    ITEM_REGISTRY = shared.registry.get_by_name("minecraft:item")

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        if not tracker.has(1):
            return False

        element = tracker.get()
        name = element.split("[")[0]

        return self.ITEM_REGISTRY.is_valid_key(name)

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        element = tracker.get()
        tracker.increase(1)
        name = element.split("[")[0]
        entry = self.ITEM_REGISTRY.get(name)()

        if "[" in element:
            logger.println(
                "[COMMAND PARSER][WARN] unimplemented feature found: item with meta data"
            )
            # todo: implement

        tracker.collect(entry)

    def __eq__(self, other):
        return isinstance(other, Block)


class Selector(ICommandElementIdentifier):
    """
    A selector, to select entities in the world
    """

    SELECTORS = {
        # Something fancy, double lambdas! Outer for creating from string, inner for execution
        # first is meta-mode; 0 is no meta, 1 optional, and 2 forced
        # type 0 takes only a single lambda, as it is not fed with the meta string
        "@s": (0, lambda env: (env.get_this(),)),
        "@p": (0, lambda env: (env.get_this(),)),  # todo: use nearest player
        "@a": (0, lambda env: list(env.get_dimension().get_world().player_iterator())),
        "@r": (
            0,
            lambda env: (
                random.choice(env.get_dimension().get_world().player_iterator()),
            ),
        ),
        # todo: use also meta-data
        "@e": (
            1,
            lambda string: lambda env: list(
                env.get_dimension().get_world().entity_iterator()
            ),
        ),
    }

    def __init__(self, max_entities=-1):
        self.max_entities = max_entities

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        string = tracker.get()
        pre = string.split("[")[0]
        if pre not in self.SELECTORS:
            return False

        meta_mode, transformer = self.SELECTORS[pre]
        if meta_mode == 0 and "[" in string:
            return False
        if meta_mode == 2 and "[" not in string:
            return False

        return True

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        string = tracker.get()
        tracker.increase(1)
        pre = string.split("[")[0]

        meta_mode, transformer = self.SELECTORS[pre]

        meta = None if "[" not in string else "[".join(string.split("[")[1:])[:-1]

        # todo: check limit
        f = transformer(meta) if meta_mode != 0 else transformer
        tracker.collect(f)

    def __eq__(self, other):
        return isinstance(other, Selector)


class AnyString(ICommandElementIdentifier):
    INSTANCE: typing.Optional["AnyString"] = None

    def __init__(self):
        self.opened = False

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return True

    def parse(self, node: "CommandNode", tracker: CommandExecutionTracker):
        if self.opened:
            string = []
            while tracker.has(1):
                string.append(tracker.get())
                tracker.increase(1)
            tracker.collect(" ".join(string))
        else:
            tracker.collect(tracker.increase(1).get(-1))

    def open(self):
        self.opened = True
        return self


AnyString.INSTANCE = AnyString()


class CommandNode:
    """
    A node in the tree of a command
    """

    def __init__(self, inner_identifier: ICommandElementIdentifier):
        self.inner_identifier = inner_identifier
        self.following_nodes: typing.List["CommandNode"] = []
        self.on_execution_callbacks = []
        self.name = "unknown"
        self.info_text = ""
        self.handles = []

    def than(self, node: "CommandNode"):
        """
        Adds a internal node into the system
        :param node: the node to add
        """
        self.following_nodes.append(node)
        return self

    def on_execution(self, func: typing.Callable):
        self.on_execution_callbacks.append(func)
        return self

    def of_name(self, name: str):
        self.name = name
        return self

    def info(self, text: str):
        self.info_text = text
        return self

    def with_handle(
        self, error: typing.Type[Exception], message_formatter: typing.Callable
    ):
        self.handles.append((error, message_formatter))
        return self

    def get_executing_node(
        self, tracker: CommandExecutionTracker
    ) -> typing.Optional["CommandNode"]:
        """
        Parsing method for parsing a CommandExecutionTracker
        :param tracker: the tracker
        :return: when arrival, the end CommandNode for execution
        """
        if not self.inner_identifier.is_valid(self, tracker):
            tracker.parsing_errors.append(
                f"node '{self.name}' using entry {self.inner_identifier}"
            )
            return

        tracker.save()
        self.inner_identifier.parse(self, tracker)

        # Are we out of data?
        if not tracker.has(1):
            return self if self.on_execution_callbacks else None

        for node in self.following_nodes:
            aft = node.get_executing_node(tracker)
            if aft is not None:
                return aft

        tracker.rollback()

    def get_similar_node(self, node: "CommandNode") -> typing.Optional["CommandNode"]:
        """
        Helper method for getting a similar node down the tree
        Similar nodes have the same inner identifier. The rest is currently ignored
        WARNING: currently, recursive trees may crash

        :param node: the node to compare to
        :return: the node or None
        """

        if self.inner_identifier == node.inner_identifier:
            return self

        for entry in self.following_nodes:
            # todo: check for circular calls
            track = entry.get_similar_node(node)
            if track is not None:
                return track

    def run(self, env, data):
        try:
            for func in self.on_execution_callbacks:
                func(env, data)

        except Exception as e:
            for compare, handle in self.handles:
                if isinstance(e, compare):
                    env.chat.print_ln(handle(env, data, e))
                    break
            else:
                raise


class Command(CommandNode):
    """
    The "base"-Node. It contains a little bit more meta-information, otherwise it is simply a normal CommandNode

    <name> is without the / in front
    """

    def __init__(self, name: str):
        super().__init__(DefinedString("/" + name))
        self.name = name
        self.additional_names = []

    def alias(self, name: str):
        self.additional_names.append(name)
        return self
