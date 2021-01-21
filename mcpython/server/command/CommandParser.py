"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

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
    main class for parsing an command
    """

    def __init__(self):
        self.commandparsing = {}  # start -> (Command, ParseBridge)

    def add_command(self, command: mcpython.server.command.Command):
        """
        register an command
        :param command: the command to add
        """
        parsebridge = mcpython.server.command.Command.ParseBridge(command)
        if not shared.event_handler.call_cancelable(
            "registry:commands:register", command, parsebridge
        ):
            return
        for entry in (
            [parsebridge.main_entry]
            if type(parsebridge.main_entry) == str
            else parsebridge.main_entry
        ):
            self.commandparsing[entry] = (command, parsebridge)

    def parse(self, command: str, info=None):
        """
        pase an command
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
        if pre[1:] in self.commandparsing:  # is it registered?
            command, parsebridge = self.commandparsing[pre[1:]]
            try:
                values, trace = self._convert_to_values(split, parsebridge, info)
            except:
                logger.print_exception(
                    "[CHAT][EXCEPTION] during parsing values for command '{}'".format(
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
                    "[CHAT][EXCEPTION] during executing command '{}' with {}".format(
                        command.NAME, info
                    )
                )
        else:
            logger.println(
                "[CHAT][COMMANDPARSER][ERROR] unknown command '{}'".format(pre)
            )

    def _convert_to_values(self, command, parsebridge, info, index=1) -> tuple:
        """
        parse command into values that can be than executed
        :param command: the command to parse
        :param parsebridge: the command info to use
        :param info: the info to use
        :param index: the index to start on
        """
        if len(command) == 1 and not any(
            [
                subcommand.mode == mcpython.server.command.Command.ParseMode.OPTIONAL
                for subcommand in parsebridge.sub_commands
            ]
        ):
            logger.println(
                "unable to parse command {}. please use /help <command name> command to get exact command "
                "syntax".format(command)
            )
            return None, None
        active_entry = parsebridge
        values = []
        array = [parsebridge]
        commandregistry = shared.registry.get_by_name("minecraft:command")
        while len(active_entry.sub_commands) > 0 and index < len(
            command
        ):  # iterate over the whole command
            flag1 = False
            for (
                subcommand
            ) in (
                active_entry.sub_commands
            ):  # go through all commands and check if valid
                if not flag1 and commandregistry.command_entries[
                    subcommand.type
                ].is_valid(
                    command, index, subcommand.args, subcommand.kwargs
                ):  # is valid
                    array.append(
                        (subcommand, active_entry.sub_commands.index(subcommand))
                    )
                    active_entry = subcommand
                    index, value = commandregistry.command_entries[
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
                        "[CHAT][COMMANDPARSER][ERROR] can't parse command, missing entry at position {}:".format(
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
            "command is not ended correct. please look at the command syntax."
        )
        return None, array


shared.command_parser = CommandParser()
