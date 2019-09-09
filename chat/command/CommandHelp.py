"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import SubCommand, ParseType, ParseMode, ParseBridge


@G.registry
class CommandHelp(chat.command.Command.Command):
    """
    class for /help command
    """

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
                print("[CHAT][COMMANDPARSER][ERROR] value must be greater than 0")
                return
            # if start >= len(PAGES):
            #    print("[CHAT][COMMANDPARSER][ERROR] value must be smaller than {}".
            #          format((len(PAGES)+1)//LINES_PER_PAGE+1))
            #    return
            if end >= len(PAGES):
                end = len(PAGES)
            pages = PAGES[start-1:end]
            print("--------------" + "-" * len(str(page)))
            print("- HELP PAGE {} -".format(page))
            print("--------------" + "-" * len(str(page)))
            print("\n".join([x[1] for x in pages]))
        elif type(values[0]) == str:
            c: str = values[0]
            if c.startswith("/"): c = c[1:]
            if c not in G.commandhandler.commands:
                print("[CHAT][COMMANDPARSER][ERROR] unknown command for help pages {}.".format(c))
                return
            print("------------------"+"-"*len(c))
            print("- HELP PAGE FOR {} -".format(c))
            print("------------------"+"-"*len(c))
            print("\n".join([x[1] for x in G.commandhandler.commands[c].get_help()]))

    @staticmethod
    def get_help() -> list:
        return ["/help [<page>: default=1]: returns the help at the given page",
                "/help <command>: returns help for given command if found"]


# generate help pages
PAGES = []
for command, _ in G.commandparser.commandparsing.values():
    PAGES += command.get_help()

PAGES.sort(key=lambda x: x[0])

LINES_PER_PAGE = 10

