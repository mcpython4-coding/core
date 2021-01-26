"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import typing

from mcpython import shared, logger
import mcpython.server.command.Command


class ParsingCommandInfo:
    """
    Info which stores information about the active executed command
    Shared across commands wherever possible

    todo: add reset system, so we don't need to copy every time
    """

    def __init__(self, entity=None, position=None, dimension=None, chat=None):
        self.entity = entity if entity else shared.world.get_active_player()
        self.position = position if position else self.entity.position
        self.dimension = (
            (dimension if dimension is not None else self.entity.dimension.id)
            if self.entity.dimension is not None
            else 0
        )
        self.chat = chat if chat is not None else shared.chat

        # for the future... todo: implement this
        # this will hold local variables
        # /execute store target-able and /execute set <name> <value> able
        # /execute if/unless var <name> defined
        # /execute if/unless var <name> >/</>=/<=/==
        # /execute with <name> copied <var name>
        # /execute with <name> static <value>
        # /variable <name> store result <expression>
        # /variable <name> store position x/y/z [<selector>/<position>]
        # /variable operate <target var> <expression name> <... args>
        # /return <value or variable>
        # /variable <name> delete
        # /variable <name> copy [to/from (default)] <var>
        # /function <name> [store <var name>] ...: <param name> copied <var name> / static <value>
        # access-able via something like <var name> in commands (-> custom entry parser!)
        self.local_variable_stack = {}
        # todo: classes? (-> dynamic registries -> block & item creation?)

    def copy(self, include_variables=False) -> "ParsingCommandInfo":
        """
        :param include_variables: if the local variable table should be copied
        :return: a copy of itself
        """
        instance = ParsingCommandInfo(
            entity=self.entity,
            position=self.position,
            dimension=self.dimension,
            chat=self.chat,
        )

        if include_variables:
            instance.local_variable_stack = self.local_variable_stack.copy()

        return instance

    def __str__(self):
        return "ParsingCommandInfo(entity={},position={},dimension={},local_variable_stack={})".format(
            self.entity, self.position, self.dimension, self.local_variable_stack
        )


class CommandParser:
    """
    Main class for parsing an command
    todo: can we pre-parse data into python text and eval it? (If we do, we must make it very secure!)
    """

    def __init__(self):
        self.command_parsing = {}  # start -> (Command, ParseBridge)

    def add_command(self, command: mcpython.server.command.Command):
        """
        register an command
        :param command: the command to add
        """
        command_syntax_holder = mcpython.server.command.Command.CommandSyntaxHolder(
            command
        )
        if not shared.event_handler.call_cancelable(
            "registry:commands:register", command, command_syntax_holder
        ):
            return

        for entry in (
            (command_syntax_holder.main_entry,)
            if type(command_syntax_holder.main_entry) == str
            else command_syntax_holder.main_entry
        ):
            self.command_parsing[entry] = (command, command_syntax_holder)

    def parse(self, command: str, info=None):
        """
        Parse an command
        :param command: the command to parse
        :param info: the info to use. can be None if one should be generated
        todo: check permission
        """
        split = command.split(" ") if type(command) == str else list(command)
        pre = split[0]
        if not info:
            info = ParsingCommandInfo()

        if not shared.event_handler.call_cancelable(
            "command:parser:execute", command, info
        ):
            return

        if pre.removeprefix("/") in self.command_parsing:  # is it registered?
            command, syntax = self.command_parsing[pre.removeprefix("/")]
            try:
                values, node_stack = self._convert_to_values(split, syntax, info)
            except:
                logger.print_exception(
                    "[CHAT][COMMAND PARSER][EXCEPTION] during parsing values for command '{}'".format(
                        command.NAME
                    )
                )
                return

            if values is None:
                return

            try:
                command.parse(values, node_stack, info)
            except:
                logger.print_exception(
                    "[CHAT][COMMAND PARSER][EXCEPTION] during executing command '{}' with {}".format(
                        command.NAME, info
                    )
                )

            if callable(node_stack[-1][0].on_node_executed):
                node_stack[-1][0].on_node_executed(info, values, node_stack)

        else:
            logger.println(
                "[CHAT][COMMAND PARSER][ERROR] unknown command '{}'".format(pre)
            )

    def _convert_to_values(
        self, command, syntax, info, index=1
    ) -> typing.Tuple[
        typing.Optional[typing.List],
        typing.Optional[typing.List[typing.Tuple[typing.Any, int]]],
    ]:
        """
        Parse command into values that can be than executed
        :param command: the command to parse
        :param syntax: the command info to use
        :param info: the info to use
        :param index: the index to start on
        :return: a tuple of the parsed values and the nodes iterated over, as (Node, node index)
        """
        if len(command) == 1 and not any(
            [
                subcommand.mode
                == mcpython.server.command.Command.CommandArgumentMode.OPTIONAL
                for subcommand in syntax.nodes
            ]
        ):
            logger.println(
                "unable to parse command {}. please use /help <command name> command to get exact command "
                "syntax".format(command)
            )
            return None, None

        active_entry = syntax
        values = []
        array = [syntax]
        command_registry = shared.registry.get_by_name("minecraft:command")

        # iterate over the whole command
        while len(active_entry.nodes) > 0 and index < len(command):
            # go through all commands and check if valid
            for node in active_entry.nodes:
                # is valid?
                if command_registry.command_entries[node.type].is_valid(
                    command, index, node.args, node.kwargs
                ):
                    array.append((node, active_entry.nodes.index(node)))
                    active_entry = node
                    index, value = command_registry.command_entries[node.type].parse(
                        command, index, info, node.args, node.kwargs
                    )
                    values.append(value)  # set value

                    if callable(node.on_node_iterated):
                        node.on_node_iterated(info, values, array)

                    break

            else:
                if all(
                    [
                        subcommand.mode
                        == mcpython.server.command.Command.CommandArgumentMode.OPTIONAL
                        for subcommand in active_entry.nodes
                    ]
                ):
                    info.chat.print_ln([x.mode for x in active_entry.nodes])
                    return values, array

                else:
                    info.chat.print_ln(
                        "[CHAT][COMMAND PARSER][ERROR] can't parse command, missing entry at position {}:".format(
                            len(array) + 1
                        )
                    )
                    info.chat.print_ln(
                        " - missing one of the following entries: {}".format(
                            [subcommand.type for subcommand in active_entry.nodes]
                        )
                    )
                    info.chat.print_ln(" - gotten values: {}".format(values))
                    return None, array

        # are all nodes optional?
        # todo: any() with correct node addition
        if all(
            [
                x.mode == mcpython.server.command.Command.CommandArgumentMode.OPTIONAL
                for x in active_entry.nodes
            ]
        ):
            return values, array

        logger.println(
            "Command is not ended correct. Please look at the command syntax via e.g. /help <command name>."
        )
        return None, array


shared.command_parser = CommandParser()
