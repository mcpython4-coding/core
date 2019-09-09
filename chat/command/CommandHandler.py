"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
import chat.command.CommandParser
import chat.command.CommandEntry
import chat.command.Selector
import event.Registry


def register_command(registry, command):
    if issubclass(command, chat.command.Command.Command):  # is it an command
        G.commandparser.add_command(command)
    elif issubclass(command, chat.command.CommandEntry.CommandEntry):  # or an command entry
        commandregistry.get_attribute("commandentries")[command.ENTRY_NAME] = command
        # print(command)
    elif issubclass(command, chat.command.Selector.Selector):  # or an selector?
        commandregistry.get_attribute("selectors").append(command)
    else:
        raise ValueError("can't register object {} to commandhandler".format(command))


commandregistry = event.Registry.Registry("command", [chat.command.Command.Command,
                                                      chat.command.CommandEntry.CommandEntry,
                                                      chat.command.Selector.Selector],
                                          injection_function=register_command)
commandregistry.set_attribute("commandentries", {})
commandregistry.set_attribute("selectors", [])

chat.command.CommandEntry.load()
chat.command.Selector.load()

from . import (CommandGive, CommandGamemode, CommandExecute, CommandKill, CommandClear, CommandTeleport, CommandReload,
               CommandGenerate, CommandSetblock, CommandFill)

# register these at the end:
from . import CommandHelp

