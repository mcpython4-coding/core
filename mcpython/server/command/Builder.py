import typing
from abc import ABC

from mcpython import logger
from mcpython import shared


class CommandExecutionTracker:
    """
    Helper code for decoding a command
    """

    @classmethod
    def from_string(cls, string: str) -> "CommandExecutionTracker":
        return cls(string.split(" "))

    def __init__(self, content=None):
        self.content = content if content is not None else []
        self.collected_values = []

        self.current_index = 0
        self.index_pool = []

        self.parsing_errors = []

    def collect(self, value):
        self.collected_values.append(value)
        return self

    def rollback(self):
        self.current_index = self.index_pool.pop(-1)

    def get(self) -> str:
        return self.content[self.current_index]

    def get_multi(self, count: int) -> typing.Iterable[str]:
        return self.content[self.current_index:self.current_index+count]

    def increase(self, count: int):
        self.current_index += count
        return self

    def save(self):
        self.index_pool.append(self.current_index)

    def has(self, count: int) -> bool:
        return len(self.content) >= self.current_index + count


class ICommandElementIdentifier(ABC):
    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        raise NotImplementedError

    def simulate(self, node: "CommandNode", tracker: CommandExecutionTracker):
        raise NotImplementedError


class DefinedString(ICommandElementIdentifier):
    def __init__(self, string: str):
        self.string = string

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return tracker.has(1) and tracker.get() == self.string

    def simulate(self, node: "CommandNode", tracker: CommandExecutionTracker):
        tracker.increase(1)
        tracker.collect(self.string)

    def __eq__(self, other):
        return isinstance(other, DefinedString) and self.string == other.string


class IntPosition(ICommandElementIdentifier):
    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return tracker.has(3) and all(
            e.removeprefix("-").isdigit() for e in tracker.get_multi(3)
        )

    def simulate(self, node: "CommandNode", tracker: CommandExecutionTracker):
        p = tracker.get_multi(3)
        tracker.increase(3)
        tracker.collect(tuple(int(e) for e in p))

    def __eq__(self, other):
        return isinstance(other, IntPosition)


class RegistryContent(ICommandElementIdentifier):
    def __init__(self, registry: str):
        self.inner_registry = shared.registry.get_by_name(registry)

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        return tracker.has(1) and self.inner_registry.is_valid_key(tracker.get())

    def simulate(self, node: "CommandNode", tracker: CommandExecutionTracker):
        key = tracker.get()
        tracker.increase(1)
        tracker.collect(self.inner_registry.get(key))

    def __eq__(self, other):
        return isinstance(other, RegistryContent) and self.inner_registry == other.inner_registry


class Block(ICommandElementIdentifier):
    BLOCK_REGISTRY = shared.registry.get_by_name("minecraft:block")

    def is_valid(self, node: "CommandNode", tracker: CommandExecutionTracker) -> bool:
        if not tracker.has(1):
            return False

        element = tracker.get()
        name = element.split("[")[0]

        return self.BLOCK_REGISTRY.is_valid_key(name)

    def simulate(self, node: "CommandNode", tracker: CommandExecutionTracker):
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

    def get_executing_node(
        self, tracker: CommandExecutionTracker
    ) -> typing.Optional["CommandNode"]:
        """
        Parsing method for parsing a CommandExecutionTracker
        :param tracker: the tracker
        :return: when arrival, the end CommandNode for execution
        """
        if not self.inner_identifier.is_valid(self, tracker):
            tracker.parsing_errors.append(f"node '{self.name}' using entry {self.inner_identifier}")
            return

        tracker.save()
        self.inner_identifier.simulate(self, tracker)

        # Are we out of data?
        if not tracker.has(1):
            return self if self.on_execution_callbacks else None

        for node in self.following_nodes:
            aft = node.get_executing_node(tracker)
            if aft is not None:
                return aft

        tracker.rollback()

    def get_similar_node(self, node: "CommandNode") -> typing.Optional["CommandNode"]:
        if self.inner_identifier == node.inner_identifier:
            return self

        for entry in self.following_nodes:
            # todo: check for circular calls
            track = entry.get_similar_node(node)
            if track is not None:
                return track


class Command(CommandNode):
    """
    The "base"-Node. It contains a little bit more meta-information
    """

    def __init__(self, name: str):
        super().__init__(DefinedString("/" + name))
        self.name = name

