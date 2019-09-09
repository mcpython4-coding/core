"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command


class ParsingCommandInfo:
    """
    info which stores information about the active executed command
    """

    def __init__(self, entity=None, position=None, dimension=None):
        self.entity = entity if entity else G.player
        self.position = position if position else G.window.position
        self.dimension = dimension if dimension is not None else 0

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

    def add_command(self, command: chat.command.Command):
        """
        register an command
        :param command: the command to add
        """
        parsebridge = chat.command.Command.ParseBridge(command)
        for entry in ([parsebridge.main_entry] if type(parsebridge.main_entry) == str else parsebridge.main_entry):
            self.commandparsing[entry] = (command, parsebridge)

    def parse(self, command: str, info=None):
        """
        pase an command
        :param command: the command to parse
        :param info: the info to use. can be None if one should be generated
        """
        splitted = command.split(" ") if type(command) == str else list(command)
        pre = splitted[0]
        if not info: info = ParsingCommandInfo()
        if pre[1:] in self.commandparsing:  # is it registered?
            command, parsebridge = self.commandparsing[pre[1:]]
            values, trace = self._convert_to_values(splitted, parsebridge, info)
            if values is None: return
            command.parse(values, trace, info)
        else:
            print("[CHAT][COMMANDPARSER][ERROR] unknown command '{}'".format(pre))

    def _convert_to_values(self, command, parsebridge, info, index=1) -> tuple:
        """
        parse command into values that can be than executed
        :param command: the command to parse
        :param parsebridge: the command info to use
        :param info: the info to use
        :param index: the index to start on
        """
        active_entry = parsebridge
        values = []
        array = [parsebridge]
        commandregistry = G.registry.get_by_name("command")
        while len(active_entry.sub_commands) > 0 and index < len(command):  # iterate over the whole command
            flag1 = False
            for subcommand in active_entry.sub_commands:  # go through all commands and check if valid
                if not flag1 and commandregistry.get_attribute("commandentries")[subcommand.type].is_valid(
                        command, index, subcommand.args, subcommand.kwargs):  # is valid
                    array.append((subcommand, active_entry.sub_commands.index(subcommand)))
                    active_entry = subcommand
                    index, value = commandregistry.get_attribute("commandentries")[subcommand.type].parse(
                        command, index, info, subcommand.args, subcommand.kwargs)
                    values.append(value)  # set value
                    flag1 = True
            if not flag1:
                if all([subcommand.mode == chat.command.Command.ParseMode.OPTIONAL for subcommand in
                        active_entry.sub_commands]):
                    return values, array
                else:
                    print("[CHAT][COMMANDPARSER][ERROR] can't parse command, missing entry at position {}".
                          format(len(array)+1))
                    print("missing one of the following entrys: {}".format([subcommand.type for subcommand in
                                                                           active_entry.sub_commands]))
                    print("gotten values: {}".format(values))
                    return None, array
        return values, array


G.commandparser = CommandParser()

