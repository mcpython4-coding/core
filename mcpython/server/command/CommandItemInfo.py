"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.server.command.Command
import mcpython.common.container.ItemStack
from mcpython.server.command.Command import ParseBridge, ParseType, SubCommand


@G.registry
class CommandItemInfo(mcpython.server.command.Command.Command):
    """
    class for /iteminfo command
    """

    NAME = "minecraft:iteminfo"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "iteminfo"
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "hand"))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "inventory"))
        parsebridge.add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "item").add_subcommand(
                SubCommand(ParseType.ITEMNAME)
            )
        )
        parsebridge.add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "block").add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "inventory").add_subcommand(
                    SubCommand(ParseType.POSITION)
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][1] == 0:  # hand
            itemstack = (
                G.world.get_active_player().get_active_inventory_slot().get_itemstack()
            )
            logger.println("info to item hold in hand")
            CommandItemInfo.print_info(itemstack)
        elif modes[1][1] == 1:  # inventory
            logger.println("[NOT IMPLEMENTED]")
        elif modes[1][1] == 2:  # from item name
            stack = mcpython.common.container.ItemStack.ItemStack(values[1])
            CommandItemInfo.print_info(stack)
        elif modes[1][1] == 3:  # block inventories
            block = info.entity.dimension.get_block(values[2])
            if type(block) == str:
                return
            for i, inventory in enumerate(block.get_inventories()):
                logger.println("inventory {}".format(i + 1))
                for si, slot in enumerate(inventory.slots):
                    if not slot.get_itemstack().is_empty():
                        logger.println("slot {}".format(si + 1))
                        CommandItemInfo.print_info(slot.get_itemstack())

    @staticmethod
    def print_info(itemstack):
        logger.println("-amount: {}".format(itemstack.amount))
        logger.println("-itemname: '{}'".format(itemstack.get_item_name()))
        if itemstack.item:
            logger.println("-has block: {}".format(itemstack.item.HAS_BLOCK))
            if itemstack.item.HAS_BLOCK:
                logger.println("-blockname: {}".format(itemstack.item.get_block()))
            logger.println(
                "-itemfile: '{}'".format(
                    itemstack.item.get_default_item_image_location()
                )
            )
            logger.println("-max stack size: {}".format(itemstack.item.STACK_SIZE))
            tags = []
            for tag in G.tag_handler.taggroups["items"].tags.values():
                if itemstack.item.NAME in tag.entries:
                    tags.append(tag.name)
            logger.println(" -tags: {}".format(tags))

    @staticmethod
    def get_help() -> list:
        return [
            "/iteminfo hand: gets info about the item in hand",
            "/iteminfo inventory: gets info about every item in inventory",
            "/iteminfo item <itemname>: gets info to an special item",
            "/iteminfo block inventory <position>: gets info about items in an block inventory",
        ]
