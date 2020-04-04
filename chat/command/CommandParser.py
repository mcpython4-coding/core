"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
import logger
import traceback


class ParsingCommandInfo:
    """
    info which stores information about the active executed command
    """

    def __init__(self, entity=None, position=None, dimension=None):
        self.entity = entity if entity else G.world.get_active_player()
        self.position = position if position else self.entity.position
        self.dimension = dimension if dimension is not None else self.entity.dimension.id

    def copy(self):
        """
        :return: a copy of itself
        """
        return ParsingCommandInfo(entity=self.entity, position=self.position, dimension=self.dimension)


class CommandParser:
    """
    main class for parsing an command
    """

    def __init__(self):
        self.commandparsing = {}  # start -> (Command, ParseBridge)
        self.CANCEL_REGISTER = False
        self.CANCEL_COMMAND_EXECUTE = False

    def add_command(self, command: chat.command.Command):
        """
        register an command
        :param command: the command to add
        """
        parsebridge = chat.command.Command.ParseBridge(command)
        self.CANCEL_REGISTER = False
        G.eventhandler.call("command:parse_bridge:setup", command, parsebridge)
        if self.CANCEL_REGISTER: return
        for entry in ([parsebridge.main_entry] if type(parsebridge.main_entry) == str else parsebridge.main_entry):
            self.commandparsing[entry] = (command, parsebridge)

    def parse(self, command: str, info=None):
        """
        pase an command
        :param command: the command to parse
        :param info: the info to use. can be None if one should be generated
        """
        split = command.split(" ") if type(command) == str else list(command)
        pre = split[0]
        if not info: info = ParsingCommandInfo()
        self.CANCEL_COMMAND_EXECUTE = False
        G.eventhandler.call("command:execute_command", info, command, split)
        if self.CANCEL_COMMAND_EXECUTE: return
        if pre[1:] in self.commandparsing:  # is it registered?
            command, parsebridge = self.commandparsing[pre[1:]]
            try:
                values, trace = self._convert_to_values(split, parsebridge, info)
            except:
                logger.println("[CHAT][EXCEPTION] during parsing values")
                logger.write_exception()
                traceback.print_exc()
                return
            if values is None: return
            try:
                command.parse(values, trace, info)
            except:
                logger.println("[CHAT][EXCEPTION] during executing command")
                logger.write_exception()
                traceback.print_exc()
        else:
            logger.println("[CHAT][COMMANDPARSER][ERROR] unknown command '{}'".format(pre))

    def _convert_to_values(self, command, parsebridge, info, index=1) -> tuple:
        """
        parse command into values that can be than executed
        :param command: the command to parse
        :param parsebridge: the command info to use
        :param info: the info to use
        :param index: the index to start on
        """
        if len(command) == 1 and not all(
                [subcommand.mode == chat.command.Command.ParseMode.OPTIONAL for subcommand in parsebridge.sub_commands]
        ):
            logger.println("unable to parse command. please use /help <command name> command to get exact command "
                           "syntax")
            return None, None
        active_entry = parsebridge
        values = []
        array = [parsebridge]
        commandregistry = G.registry.get_by_name("command")
        while len(active_entry.sub_commands) > 0 and index < len(command):  # iterate over the whole command
            flag1 = False
            for subcommand in active_entry.sub_commands:  # go through all commands and check if valid
                if not flag1 and commandregistry.commandentries[subcommand.type].is_valid(
                        command, index, subcommand.args, subcommand.kwargs):  # is valid
                    array.append((subcommand, active_entry.sub_commands.index(subcommand)))
                    active_entry = subcommand
                    index, value = commandregistry.commandentries[subcommand.type].parse(
                        command, index, info, subcommand.args, subcommand.kwargs)
                    values.append(value)  # set value
                    flag1 = True
            if not flag1:
                if all([subcommand.mode == chat.command.Command.ParseMode.OPTIONAL for subcommand in
                        active_entry.sub_commands]):
                    logger.println([x.mode for x in active_entry.sub_commands])
                    return values, array
                else:
                    logger.println("[CHAT][COMMANDPARSER][ERROR] can't parse command, missing entry at position {}:".
                                   format(len(array)+1))
                    logger.println(" - missing one of the following entries: {}".format([subcommand.type for subcommand
                                                                                         in active_entry.sub_commands]))
                    logger.println(" - gotten values: {}".format(values))
                    return None, array
        if all([x.mode == chat.command.Command.ParseMode.OPTIONAL for x in active_entry.sub_commands]):
            return values, array
        logger.println("command is not ended correct. please look at the command syntax.")
        return None, array


G.commandparser = CommandParser()

