"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
import chat.command.CommandParser
import chat.command.CommandEntry
import chat.command.Selector


class CommandHandler:
    """
    main registry for commands
    """

    def __init__(self):
        self.commands = []
        self.commandentries = {}
        self.selectors = []

    def add(self, command):
        """
        register an command to the registry
        :param command: the command to add
        :return: the command
        """
        return self(command)

    def __call__(self, command):
        """
        register an command to the registry
        :param command: the command to add
        :return: the command
        """
        if issubclass(command, chat.command.Command.Command):  # is it an command
            self.commands.append(command)
            G.commandparser.add_command(command)
        elif issubclass(command, chat.command.CommandEntry.CommandEntry):  # or an command entry
            self.commandentries[command.ENTRY_NAME] = command
        elif issubclass(command, chat.command.Selector.Selector):  # or an selector?
            self.selectors.append(command)
        else:
            raise ValueError("can't register object {} to commandhandler".format(command))
        return command


G.commandhandler = CommandHandler()


# load the stuff

chat.command.CommandEntry.load()
chat.command.Selector.load()

from . import (CommandGive, CommandGamemode, CommandExecute, CommandKill, CommandClear, CommandTeleport, CommandReload,
               CommandGenerate, CommandSetblock, CommandFill)
# register these at the end:
from . import CommandHelp

