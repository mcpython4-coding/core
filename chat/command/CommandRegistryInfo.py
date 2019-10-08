"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandRegistryInfo(chat.command.Command.Command):
    """
    command /registryinfo
    """

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "registryinfo"
        parsebridge.add_subcommand(SubCommand(ParseType.STRING_WITHOUT_QUOTES).add_subcommand(
            SubCommand(ParseType.STRING_WITHOUT_QUOTES, mode=ParseMode.OPTIONAL)))

    @staticmethod
    def parse(values: list, modes: list, info):
        registry = G.registry.get_by_name(values[0])
        if len(values) == 1:
            print("values in registry {}".format(values[0]))
            for element in registry.registered_objects:
                if hasattr(element, "get_name"):
                    print(element.get_name(), element)
                else:
                    print(element)
        else:
            print(registry.get_attribute(values[1]))

    @staticmethod
    def get_help() -> list:
        return ["/registryinfo <registry> [<attribute>]: gives info to selected registry"]

