"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandClear(chat.command.Command.Command):
    """
    command /clear
    """

    NAME = "minecraft:clear"

    CANCEL_CLEAR = False  # cancel the clear-execute

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "clear"
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        cls.CANCEL_CLEAR = False
        G.eventhandler.call("command:clear:start")
        if cls.CANCEL_CLEAR: return
        if len(values) == 0: values.append([G.world.get_active_player()])
        for entity in values[0]:
            for inventory in (entity.inventories if type(entity.inventories) in [list, set, tuple] else (
                              [entity.inventories] if type(entity.inventories) != dict else
                              entity.inventories.values())):
                for slot in inventory.slots:
                    slot.get_itemstack().clean()
            entity.xp = 0
            entity.xp_level = 0
        G.inventoryhandler.moving_slot.get_itemstack().clean()
        G.eventhandler.call("command:clear:end")

    @staticmethod
    def get_help() -> list:
        return ["/clear [<selector: entitys>: default=@s]: clear inventory of given entity(s)"]

