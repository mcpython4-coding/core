from abc import ABC
import typing
import math
import mcpython.common.world.AbstractInterface
import mcpython.util.math
from mcpython import shared
import enum


class FailType(enum.Enum):
    SYNTAX = 0  # raise InvalidSyntaxError instead!
    INTERNAL_FATAL = 1


class InvalidSyntaxError(ValueError):
    pass


class PreInvalidSyntaxError(SyntaxError):
    pass


class CommandAccess:
    ANYBODY = 0x0000
    IN_WORLD_ONLY = 0x0001
    OP_ONLY = 0x0002
    GAMEMODE_0_ONLY = 0x0004
    GAMEMODE_1_ONLY = 0x0008
    GAMEMODE_2_ONLY = 0x0010
    GAMEMODE_3_ONLY = 0x0020


class ExecutingCommandInfo:
    def __init__(self):
        self.entity = None
        self.position = None
        self.direction = None
        self.dimension: typing.Optional[
            mcpython.common.world.AbstractInterface.IDimension
        ] = None
        self.chat = None
        self.failed = False
        self.fail_info = None

    def fail_execution(self, fail_type: FailType, message: str):
        self.failed = True
        self.fail_info = (fail_type, message)

    def copy(self) -> "ExecutingCommandInfo":
        info = ExecutingCommandInfo()
        info.entity = self.entity
        info.position = self.position
        info.direction = self.direction
        info.dimension = self.dimension
        info.chat = self.chat
        return info


class CommandExecutionBuilder:
    COMMANDS: typing.List["CommandBuilder"] = []

    def __init__(self, command: str):
        self.raw_command = command.removeprefix("/")
        self.split_command = command.removeprefix("/").split(" ")
        self.current_parsing_index = 0
        self.current_data = None

    def get_current_part(self):
        if self.current_data is not None:
            return self.current_data
        if self.current_parsing_index >= len(self.split_command):
            return
        first = self.split_command[self.current_parsing_index]
        text = [first]

        # todo: implement string escaping
        # if first[0] in "\"'{[(":
        #     endian = first[0]

        self.current_data = " ".join(text)
        return self.current_data

    def next_part(self) -> int:
        if self.current_data is None:
            self.get_current_part()
        self.current_parsing_index += self.current_data.count(" ") + 1
        self.current_data = None
        return self.current_parsing_index

    def set_position(self, position: int):
        self.current_data = None
        self.current_parsing_index = position

    def run(self, context: ExecutingCommandInfo):
        for command in self.COMMANDS:
            if command.matches(self):
                self.execute_as_command(command, context)
                break
        else:
            raise InvalidSyntaxError("command not found")

    def execute_as_command(
        self, command: "CommandBuilder", context: ExecutingCommandInfo
    ):
        assert command.matches(self), "command must be matching"
        tree = command.select_tree(self)
        self.set_position(0)
        for i, matcher in enumerate(tree[:-1]):
            matcher.parse(self, context, tree)
            if context.failed and context.fail_info[0] == FailType.SYNTAX:
                raise InvalidSyntaxError(context.fail_info[1])
            self.next_part()
        tree[-1].parse(self, context, tree, is_end=True)
        if context.failed and context.fail_info[0] == FailType.SYNTAX:
            raise InvalidSyntaxError(context.fail_info[1])


class ICommandMatcher(ABC):
    def __init__(self, access: int = CommandAccess.ANYBODY):
        self.access = access
        self.following: typing.List["ICommandMatcher"] = []
        self.on_end = None
        self.on_between = None

    def add_subsequent_stage(self, stage: "ICommandMatcher"):
        self.following.append(stage)
        return self

    def add_subsequent_stages(self, stages: typing.List["ICommandMatcher"]):
        self.following += stages
        return self

    def execute_on_end(self, callback: typing.Callable):
        self.on_end = callback
        return self

    def execute_on_between(self, callback: typing.Callable):
        self.on_between = callback
        return self

    def matches(self, builder: CommandExecutionBuilder) -> bool:
        raise NotImplementedError()

    def select_tree(
        self, builder: CommandExecutionBuilder
    ) -> typing.List["ICommandMatcher"]:
        if len(self.following) == 0:
            if builder.get_current_part() is None:
                return [self]
            raise PreInvalidSyntaxError("unexpected command end")
        state = builder.next_part()
        exceptions = []
        for matcher in self.following:
            if matcher.matches(builder):
                try:
                    tree = matcher.select_tree(builder)
                except PreInvalidSyntaxError as e:
                    exceptions.append(e)
                else:
                    return [self] + tree
            builder.set_position(state)
        if self.on_end is not None:
            return [self]
        raise InvalidSyntaxError(
            "did not find end, the following errors where found: {}".format(exceptions)
        )

    def parse(
        self,
        builder: CommandExecutionBuilder,
        context: ExecutingCommandInfo,
        tree: typing.List["ICommandMatcher"],
        is_end=False,
    ):
        if not is_end:
            if callable(self.on_between):
                self.on_between(self, builder, context, tree)
        else:
            if callable(self.on_end):
                self.on_end(self, builder, context, tree)
            else:
                raise InvalidSyntaxError("did not expect command end")


class TextMatcher(ICommandMatcher):
    def __init__(self, text: str, access: int = CommandAccess.ANYBODY):
        super().__init__(access)
        self.text = text

    def matches(self, builder: CommandExecutionBuilder) -> bool:
        return builder.get_current_part() == self.text


class IntMatcher(ICommandMatcher):
    def __init__(
        self,
        data_range: typing.Union[
            typing.Tuple[int, int],
            typing.Callable[[CommandExecutionBuilder, int], bool],
        ] = (-math.inf, math.inf),
        access: int = CommandAccess.ANYBODY,
    ):
        super().__init__(access)
        self.data_range = data_range
        self.value = None

    def matches(self, builder: CommandExecutionBuilder) -> bool:
        data = mcpython.util.math.try_parse_int(builder.get_current_part())
        if data is None:
            return False
        if callable(self.data_range):
            return self.data_range(builder, data)
        return self.data_range[0] <= data <= self.data_range[1]

    def parse(
        self,
        builder: CommandExecutionBuilder,
        context: ExecutingCommandInfo,
        tree: typing.List["ICommandMatcher"],
        is_end=False,
    ):
        self.value = mcpython.util.math.try_parse_int(builder.get_current_part())
        super().parse(builder, context, tree, is_end=is_end)


class FloatMatcher(ICommandMatcher):
    def __init__(
        self,
        data_range: typing.Union[
            typing.Tuple[float, float],
            typing.Callable[[CommandExecutionBuilder, float], bool],
        ] = (-math.inf, math.inf),
        access: int = CommandAccess.ANYBODY,
    ):
        super().__init__(access)
        self.data_range = data_range
        self.value = None

    def matches(self, builder: CommandExecutionBuilder) -> bool:
        data = mcpython.util.math.try_parse_float(builder.get_current_part())
        if data is None:
            return False
        if callable(self.data_range):
            return self.data_range(builder, data)
        return self.data_range[0] <= data <= self.data_range[1]

    def parse(
        self,
        builder: CommandExecutionBuilder,
        context: ExecutingCommandInfo,
        tree: typing.List["ICommandMatcher"],
        is_end=False,
    ):
        self.value = mcpython.util.math.try_parse_float(builder.get_current_part())
        super().parse(builder, context, tree, is_end=is_end)


class SelectorMatcher(ICommandMatcher):
    def __init__(
        self,
        allowed_entity_tags=None,
        disallowed_entity_tags=None,
        max_entity_count=math.inf,
        access: int = CommandAccess.ANYBODY,
    ):
        super().__init__(access)
        self.allowed_entity_tags = allowed_entity_tags
        self.disallowed_entity_tags = disallowed_entity_tags
        self.max_entity_count = max_entity_count
        self.entity = None

    def matches(self, builder: CommandExecutionBuilder) -> bool:
        return builder.get_current_part().startswith("@")

    def parse(
        self,
        builder: CommandExecutionBuilder,
        context: ExecutingCommandInfo,
        tree,
        is_end=False,
    ):
        string = builder.get_current_part()
        if string == "@s":
            self.entity = context.entity
        elif string == "@p":
            self.entity = context.dimension.get_world().nearest_player(
                context.position, context.dimension
            )
        elif string == "@a":
            players = context.dimension.get_world().player_iterator()
            if len(players) != 1:
                raise InvalidSyntaxError("selector must select EXACTLY one player")
            self.entity = players[0]
        else:
            raise InvalidSyntaxError("selector {} not found!".format(string))
        super().parse(builder, context, tree, is_end=is_end)


class PositionMatcher(ICommandMatcher):
    def __init__(self, access: int = CommandAccess.ANYBODY):
        super().__init__(access)
        self.position = None

    def matches(self, builder: CommandExecutionBuilder) -> bool:
        old = builder.current_parsing_index
        a = builder.get_current_part()
        builder.next_part()
        b = builder.get_current_part()
        builder.next_part()
        c = builder.get_current_part()
        position = (a, b, c)
        if all(
            [
                e[0] in "~^" or mcpython.util.math.try_parse_int(e) is not None
                for e in position
            ]
        ):
            return True
        builder.set_position(old)
        return False

    def parse(
        self,
        builder: CommandExecutionBuilder,
        context: ExecutingCommandInfo,
        tree,
        is_end=False,
    ):
        a = builder.get_current_part()
        builder.next_part()
        b = builder.get_current_part()
        builder.next_part()
        c = builder.get_current_part()
        position = (a, b, c)
        self.position = tuple(
            [
                mcpython.util.math.try_parse_int(e)
                if e[0] not in "~^"
                else (
                    context.position[i] + mcpython.util.math.try_parse_int(e[1:])
                    if e[0] == "~"
                    else 0  # todo: implement
                )
                for i, e in enumerate(position)
            ]
        )
        super().parse(builder, context, tree, is_end=is_end)


class BlockPredicateMatcher(ICommandMatcher):
    def matches(self, builder: CommandExecutionBuilder) -> bool:
        name = builder.get_current_part()
        return name in shared.registry.get_by_name("block").full_entries or (
            name.startswith("#") and name in shared.taghandler.taggroups["blocks"].tags
        )


class CommandBuilder(ICommandMatcher):
    def __init__(self, base_name: str, access: int = CommandAccess.ANYBODY):
        super().__init__(access)
        self.base_name = base_name.removeprefix("/")
        CommandExecutionBuilder.COMMANDS.append(self)

    def matches(self, builder: CommandExecutionBuilder) -> bool:
        return builder.get_current_part() == self.base_name


def load_commands():
    from . import CommandClear, CommandClone
