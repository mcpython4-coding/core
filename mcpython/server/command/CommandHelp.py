"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    SubCommand,
    ParseType,
    ParseMode,
    ParseBridge,
)


@shared.registry
class CommandHelp(mcpython.server.command.Command.Command):
    """
    class for /help command
    """

    NAME = "minecraft:help"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["help", "?"]
        parsebridge.add_subcommand(
            SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL)
        ).add_subcommand(SubCommand(ParseType.STRING, mode=ParseMode.OPTIONAL))

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0:
            values.append(1)
        if type(values[0]) == int:
            page: int = values[0]
            start = (page - 1) * LINES_PER_PAGE
            end = start + LINES_PER_PAGE - 1
            if start < 0:
                logger.println(
                    "[CHAT][COMMANDPARSER][ERROR] value must be greater than 0"
                )
                return
            if end >= len(PAGES):
                end = len(PAGES)
            pages = PAGES[start - 1 if start != 0 else 0 : end]
            logger.println("--------------" + "-" * len(str(page)))
            logger.println("- HELP PAGE {} -".format(page))
            logger.println("--------------" + "-" * len(str(page)))
            logger.println("\n".join(pages))
        elif type(values[0]) == str:
            c: str = values[0]
            if c.startswith("/"):
                c = c[1:]
            if c not in shared.registry.get_by_name("minecraft:command").command_entries:
                logger.println(
                    "[CHAT][COMMAND PARSER][ERROR] unknown command for help pages {}.".format(
                        c
                    )
                )
                return
            logger.println("------------------" + "-" * len(c))
            logger.println("- HELP PAGE FOR {} -".format(c))
            logger.println("------------------" + "-" * len(c))
            logger.println(
                "\n".join(
                    shared.registry.get_by_name("minecraft:command")
                    .command_entries[c]
                    .get_help()
                )
            )

    @staticmethod
    def get_help() -> list:
        return [
            "/help [<page>: default=1]: returns the help at the given page",
            "/help <command>: returns help for given command if found",
        ]


# generate help pages  todo: change to an loading stage
PAGES = []
for command, _ in shared.command_parser.commandparsing.values():
    h = command.get_help()
    PAGES += h if type(h) == list else [h]

shared.event_handler.call("command:help:generate_pages", PAGES)

PAGES.sort(key=lambda x: x.split(" ")[0])

LINES_PER_PAGE = 10  # an internal config, can be changed
