"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import chat.command.Command
import chat.command.CommandParser


class CommandHandler:
    def __init__(self):
        self.commands = []

    def add(self, command):
        self(command)

    def __call__(self, command):
        self.commands.append(command)
        G.commandparser.add_command(command)


G.commandhandler = CommandHandler()


from . import (CommandGive, CommandGamemode)

