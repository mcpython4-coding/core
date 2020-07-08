"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import logger
import mcpython.chat.command.Command
from mcpython.chat.command.Command import ParseBridge, ParseType, SubCommand


@G.registry
class CommandRegistryInfo(mcpython.chat.command.Command.Command):
    """
    command /registryinfo
    """

    NAME = "minecraft:registry_info"

    CANCEL_REGISTRY_INFO = False

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "registryinfo"
        parsebridge.add_subcommand(SubCommand(ParseType.STRING_WITHOUT_QUOTES))

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
            for key in registry.registered_object_map.keys():
                element = registry.registered_object_map[key]
                logger.println(key, element, element.INFO, sep=" ")

    @staticmethod
    def get_help() -> list:
        return ["/registryinfo <registry> [<attribute>]: gives info to selected registry"]

