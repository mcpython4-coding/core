"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandClear(chat.command.Command.Command):
    """
    command /clear
    """

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "clear"
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL))

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0: values.append([G.player])
        for entity in values[0]:
            for inventory in (entity.inventorys if type(entity.inventorys) in [list, set, tuple] else (
                              [entity.inventorys] if type(entity.inventorys) != dict else entity.inventorys.values())):
                for slot in inventory.slots:
                    slot.itemstack.clean()
            entity.xp = 0
            entity.xp_level = 0

    @staticmethod
    def get_help() -> list:
        return ["/clear [<selector: entitys>: default=@s]: clear inventory of given entity(s)"]

