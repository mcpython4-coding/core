"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, SubCommand, ParseMode


@G.commandhandler
class CommandGamemode(chat.command.Command.Command):
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "0").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "1").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "2").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "3").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "survival").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "creative").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "adventure").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "spectator").add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)))
        parsebridge.main_entry = "gamemode"

    @staticmethod
    def parse(values: list, modes: list):
        mode = values[0]
        (G.player if len(values) == 1 else values[1]).set_gamemode(mode)

