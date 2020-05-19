"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

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
        parsebridge.add_subcommand(ParseType.SELECTOR.set_mode(ParseMode.OPTIONAL))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        cls.CANCEL_CLEAR = False
        G.eventhandler.call("command:clear:start")
        if cls.CANCEL_CLEAR: return
        if len(values) == 0: values.append([G.world.get_active_player()])
        for entity in values[0]:  # iterate over all entities
            if not hasattr(entity, "inventories"):  # has it an inventory?
                G.chat.print_ln("entity {} has no inventories!".format(entity))
                continue
            for inventory in entity.get_inventories():
                inventory.clear()  # clear every inventory
            if hasattr(entity, "xp"):
                entity.xp = 0
                entity.xp_level = 0
        G.inventoryhandler.moving_slot.get_itemstack().clean()
        G.eventhandler.call("command:clear:end")

    @staticmethod
    def get_help() -> list:
        return ["/clear [<selector: entitys>: default=@s]: clear inventory of given entity(s)"]

