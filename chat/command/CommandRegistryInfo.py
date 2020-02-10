"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import logger


@G.registry
class CommandRegistryInfo(chat.command.Command.Command):
    """
    command /registryinfo
    """

    CANCEL_REGISTRY_INFO = False

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "registryinfo"
        parsebridge.add_subcommand(SubCommand(ParseType.STRING_WITHOUT_QUOTES).add_subcommand(
            SubCommand(ParseType.STRING_WITHOUT_QUOTES, mode=ParseMode.OPTIONAL)))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        cls.CANCEL_REGISTRY_INFO = False
        G.eventhandler.call("command:registryinfo:parse", values[0])
        if cls.CANCEL_REGISTRY_INFO: return
        registry = G.registry.get_by_name(values[0])
        if registry is None:
            logger.println("[CHAT][ERROR] selected unknown registry: '{}'".format(values[0]))
            return
        if len(values) == 1:
            logger.println("values in registry {}".format(values[0]))
            for element in registry.registered_objects:
                if hasattr(element, "get_name"):
                    logger.println(element.get_name(), element)
                else:
                    logger.println(element)
        else:
            logger.println(registry.get_attribute(values[1]))

    @staticmethod
    def get_help() -> list:
        return ["/registryinfo <registry> [<attribute>]: gives info to selected registry"]

