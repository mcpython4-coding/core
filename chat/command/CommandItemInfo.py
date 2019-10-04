"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import gui.ItemStack


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
            itemstack = G.player.get_active_inventory_slot().itemstack
            print("info to item hold in hand")
            CommandItemInfo.print_info(itemstack)
        elif modes[1][1] == 1:  # inventory
            for inventorykey in G.player.inventorys.keys():
                print("info to inventory {} of player".format(inventorykey))
                for i, slot in enumerate(G.player.inventorys[inventorykey].slots):
                    if not slot.itemstack.is_empty():
                        print("slot {}".format(i+1))
                        CommandItemInfo.print_info(slot.itemstack)
        elif modes[1][1] == 2:  # from item name
            stack = gui.ItemStack.ItemStack(values[1])
            CommandItemInfo.print_info(stack)
        elif modes[1][1] == 3:  # block inventories
            block = G.world.get_active_dimension().get_block(values[2])
            if type(block) == str: return
            for i, inventory in enumerate(block.get_inventories()):
                print("inventory {}".format(i+1))
                for si, slot in enumerate(inventory.slots):
                    if not slot.itemstack.is_empty():
                        print("slot {}".format(si+1))
                        CommandItemInfo.print_info(slot.itemstack)

    @staticmethod
    def print_info(itemstack):
        print("-amount: {}".format(itemstack.amount))
        print("-itemname: '{}'".format(itemstack.get_item_name()))
        if itemstack.item:
            print("-has block: {}".format(itemstack.item.has_block()))
            if itemstack.item.has_block():
                print("-blockname: {}".format(itemstack.item.get_block()))
            print("-itemfile: '{}'".format(itemstack.item.get_item_image_location()))
            print("-max stack size: {}".format(itemstack.item.get_max_stack_size()))

    @staticmethod
    def get_help() -> list:
        return ["/iteminfo hand: gets info about the item in hand",
                "/iteminfo inventory: gets info about every item in inventory",
                "/iteminfo item <itemname>: gets info to an special item",
                "/iteminfo block inventory <position>: gets info about items in an block inventory"]

