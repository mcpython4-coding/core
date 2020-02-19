"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import gui.ItemStack
import logger


@G.registry
class CommandItemInfo(chat.command.Command.Command):
    """
    class for /iteminfo command
    """

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "iteminfo"
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "hand"))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "inventory"))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "item").add_subcommand(SubCommand(
            ParseType.ITEMNAME)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "block").add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "inventory").add_subcommand(SubCommand(ParseType.POSITION))))

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][1] == 0:  # hand
            itemstack = G.player.get_active_inventory_slot().get_itemstack()
            logger.println("info to item hold in hand")
            CommandItemInfo.print_info(itemstack)
        elif modes[1][1] == 1:  # inventory
            for inventorykey in G.player.inventorys.keys():
                logger.println("info to inventory {} of player".format(inventorykey))
                for i, slot in enumerate(G.player.inventorys[inventorykey].slots):
                    if not slot.get_itemstack().is_empty():
                        logger.println("slot {}".format(i+1))
                        CommandItemInfo.print_info(slot.get_itemstack())
        elif modes[1][1] == 2:  # from item name
            stack = gui.ItemStack.ItemStack(values[1])
            CommandItemInfo.print_info(stack)
        elif modes[1][1] == 3:  # block inventories
            block = G.world.get_active_dimension().get_block(values[2])
            if type(block) == str: return
            for i, inventory in enumerate(block.get_inventories()):
                logger.println("inventory {}".format(i+1))
                for si, slot in enumerate(inventory.slots):
                    if not slot.get_itemstack().is_empty():
                        logger.println("slot {}".format(si+1))
                        CommandItemInfo.print_info(slot.get_itemstack())

    @staticmethod
    def print_info(itemstack):
        logger.println("-amount: {}".format(itemstack.amount))
        logger.println("-itemname: '{}'".format(itemstack.get_item_name()))
        if itemstack.item:
            logger.println("-has block: {}".format(itemstack.item.has_block()))
            if itemstack.item.has_block():
                logger.println("-blockname: {}".format(itemstack.item.get_block()))
            logger.println("-itemfile: '{}'".format(itemstack.item.get_default_item_image_location()))
            logger.println("-max stack size: {}".format(itemstack.item.get_max_stack_size()))
            tags = []
            for tag in G.taghandler.taggroups["items"].tags.values():
                if itemstack.item.NAME in tag.entries:
                    tags.append(tag.name)
            logger.println(" -tags: {}".format(tags))

    @staticmethod
    def get_help() -> list:
        return ["/iteminfo hand: gets info about the item in hand",
                "/iteminfo inventory: gets info about every item in inventory",
                "/iteminfo item <itemname>: gets info to an special item",
                "/iteminfo block inventory <position>: gets info about items in an block inventory"]

