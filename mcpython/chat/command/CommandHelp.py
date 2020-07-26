"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import logger
import mcpython.chat.command.Command
from mcpython.chat.command.Command import SubCommand, ParseType, ParseMode, ParseBridge


@G.registry
class CommandHelp(mcpython.chat.command.Command.Command):
    """
    class for /help command
    """

    NAME = "minecraft:help"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["help", "?"]
        parsebridge.add_subcommand(
            SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL)
        ).add_subcommand(
            SubCommand(ParseType.STRING, mode=ParseMode.OPTIONAL)
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0: values.append(1)
        if type(values[0]) == int:
            page: int = values[0]
            start = (page - 1) * LINES_PER_PAGE
            end = start + LINES_PER_PAGE - 1
            if start < 0:
                logger.println("[CHAT][COMMANDPARSER][ERROR] value must be greater than 0")
                return
            if end >= len(PAGES):
                end = len(PAGES)
            pages = PAGES[start-1 if start != 0 else 0:end]
            logger.println("--------------" + "-" * len(str(page)))
            logger.println("- HELP PAGE {} -".format(page))
            logger.println("--------------" + "-" * len(str(page)))
            logger.println("\n".join(pages))
        elif type(values[0]) == str:
            c: str = values[0]
            if c.startswith("/"): c = c[1:]
            if c not in G.registry.get_by_name("command").commandentries:
                logger.println("[CHAT][COMMANDPARSER][ERROR] unknown command for help pages {}.".format(c))
                return
            logger.println("------------------"+"-"*len(c))
            logger.println("- HELP PAGE FOR {} -".format(c))
            logger.println("------------------"+"-"*len(c))
            logger.println("\n".join(G.registry.get_by_name("command").commandentries[c].get_help()))

    @staticmethod
    def get_help() -> list:
        return ["/help [<page>: default=1]: returns the help at the given page",
                "/help <command>: returns help for given command if found"]


# generate help pages  todo: change to an loading stage
PAGES = []
for command, _ in G.commandparser.commandparsing.values():
    h = command.get_help()
    PAGES += h if type(h) == list else [h]

G.eventhandler.call("command:help:generate_pages", PAGES)

PAGES.sort(key=lambda x: x.split(" ")[0])

LINES_PER_PAGE = 10  # an internal config, can be changed

