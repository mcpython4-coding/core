"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.server.command.Command


class ParsingCommandInfo:
    """
    info which stores information about the active executed command
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
        # /execute if var <name> defined
        # /execute if var <name> >/</>=/<=/==
        # /variable <name> store result <expression>
        # /variable <name> store position x/y/z [<selector>/<position>]
        # /operation target <expression name> <... args>
        # /return <value or variable>
        # /variable <name> delete
        # /variable <name> copy [to/from (default)] <var>
        # access-able via something like <var name> in commands (-> custom entry parser!)
        self.local_variable_stack = {}
        # todo: add some way for invoking function & getting returned result
        # todo: add way to invoke function with parameters
        # todo: classes? (-> dynamic registries -> block & item creation?)

    def copy(self):
        """
        :return: a copy of itself
        """
        return ParsingCommandInfo(
            entity=self.entity,
            position=self.position,
            dimension=self.dimension,
            chat=self.chat,
        )

    def __str__(self):
        return "ParsingCommandInfo(entity={},position={},dimension={})".format(
            self.entity, self.position, self.dimension
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
        parse_bridge = mcpython.server.command.Command.ParseBridge(command)
        if not shared.event_handler.call_cancelable(
            "registry:commands:register", command, parse_bridge
        ):
            return
        for entry in (
            [parse_bridge.main_entry]
            if type(parse_bridge.main_entry) == str
            else parse_bridge.main_entry
        ):
            self.command_parsing[entry] = (command, parse_bridge)

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
        if pre[1:] in self.command_parsing:  # is it registered?
            command, parsebridge = self.command_parsing[pre[1:]]
            try:
                values, trace = self._convert_to_values(split, parsebridge, info)
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
                command.parse(values, trace, info)
            except:
                logger.print_exception(
                    "[CHAT][COMMAND PARSER][EXCEPTION] during executing command '{}' with {}".format(
                        command.NAME, info
                    )
                )

        else:
            logger.println(
                "[CHAT][COMMAND PARSER][ERROR] unknown command '{}'".format(pre)
            )

    def _convert_to_values(self, command, parse_bridge, info, index=1) -> tuple:
        """
        parse command into values that can be than executed
        :param command: the command to parse
        :param parse_bridge: the command info to use
        :param info: the info to use
        :param index: the index to start on
        """
        if len(command) == 1 and not any(
            [
                subcommand.mode == mcpython.server.command.Command.ParseMode.OPTIONAL
                for subcommand in parse_bridge.sub_commands
            ]
        ):
            logger.println(
                "unable to parse command {}. please use /help <command name> command to get exact command "
                "syntax".format(command)
            )
            return None, None
        active_entry = parse_bridge
        values = []
        array = [parse_bridge]
        command_registry = shared.registry.get_by_name("minecraft:command")
        while len(active_entry.sub_commands) > 0 and index < len(
            command
        ):  # iterate over the whole command
            flag1 = False
            for (
                subcommand
            ) in (
                active_entry.sub_commands
            ):  # go through all commands and check if valid
                if not flag1 and command_registry.command_entries[
                    subcommand.type
                ].is_valid(
                    command, index, subcommand.args, subcommand.kwargs
                ):  # is valid
                    array.append(
                        (subcommand, active_entry.sub_commands.index(subcommand))
                    )
                    active_entry = subcommand
                    index, value = command_registry.command_entries[
                        subcommand.type
                    ].parse(command, index, info, subcommand.args, subcommand.kwargs)
                    values.append(value)  # set value
                    flag1 = True
            if not flag1:
                if all(
                    [
                        subcommand.mode
                        == mcpython.server.command.Command.ParseMode.OPTIONAL
                        for subcommand in active_entry.sub_commands
                    ]
                ):
                    logger.println([x.mode for x in active_entry.sub_commands])
                    return values, array
                else:
                    logger.println(
                        "[CHAT][COMMAND PARSER][ERROR] can't parse command, missing entry at position {}:".format(
                            len(array) + 1
                        )
                    )
                    logger.println(
                        " - missing one of the following entries: {}".format(
                            [
                                subcommand.type
                                for subcommand in active_entry.sub_commands
                            ]
                        )
                    )
                    logger.println(" - gotten values: {}".format(values))
                    return None, array
        if all(
            [
                x.mode == mcpython.server.command.Command.ParseMode.OPTIONAL
                for x in active_entry.sub_commands
            ]
        ):
            return values, array
        logger.println(
            "Command is not ended correct. Please look at the command syntax via e.g. /help <command name>."
        )
        return None, array


shared.command_parser = CommandParser()
