"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.server.command.Command
import mcpython.common.container.ItemStack
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    Node,
)


@shared.registry
class CommandItemInfo(mcpython.server.command.Command.Command):
    """
    Class for /iteminfo command
    todo: maybe merge with /blockinfo, and add entity variant
    """

    NAME = "minecraft:iteminfo"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "iteminfo"
        command_syntax_holder.add_node(Node(CommandArgumentType.DEFINED_STRING, "hand"))
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "inventory")
        )
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "item").add_node(
                Node(CommandArgumentType.ITEM_NAME)
            )
        )
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "block").add_node(
                Node(CommandArgumentType.DEFINED_STRING, "inventory").add_node(
                    Node(CommandArgumentType.POSITION)
                )
            )
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][1] == 0:  # hand
            itemstack = (
                shared.world.get_active_player()
                .get_active_inventory_slot()
                .get_itemstack()
            )
            logger.println("info to item hold in hand")
            CommandItemInfo.print_info(itemstack, info.chat.print_ln)

        elif modes[1][1] == 1:  # inventory
            logger.println("[NOT IMPLEMENTED]")

        elif modes[1][1] == 2:  # from item name
            stack = mcpython.common.container.ItemStack.ItemStack(values[1])
            CommandItemInfo.print_info(stack, info.chat.print_ln)

        elif modes[1][1] == 3:  # block inventories
            block = info.entity.dimension.get_block(values[2])
            if type(block) == str:
                return
            for i, inventory in enumerate(block.get_inventories()):
                logger.println("inventory {}".format(i + 1))
                for si, slot in enumerate(inventory.slots):
                    if not slot.get_itemstack().is_empty():
                        logger.println("slot {}".format(si + 1))
                        CommandItemInfo.print_info(
                            slot.get_itemstack(), info.chat.print_ln
                        )

    @staticmethod
    def print_info(itemstack, method=logger.println):
        method("- amount: {}".format(itemstack.amount))
        method("- item name: '{}'".format(itemstack.get_item_name()))
        if itemstack.item:
            method("- has block: {}".format(itemstack.item.HAS_BLOCK))
            if itemstack.item.HAS_BLOCK:
                method("- blockname: {}".format(itemstack.item.get_block()))
            method(
                "- item file: '{}'".format(
                    itemstack.item.get_default_item_image_location()
                )
            )
            method("- max stack size: {}".format(itemstack.item.STACK_SIZE))
            tags = []
            for tag in shared.tag_handler.taggroups["items"].tags.values():
                if itemstack.item.NAME in tag.entries:
                    tags.append(tag.name)
            method("- tags: {}".format(tags))

    @staticmethod
    def get_help() -> list:
        return [
            "/iteminfo hand: gets info about the item in hand",
            "/iteminfo inventory: gets info about every item in inventory",
            "/iteminfo item <item name>: gets info to an special item",
            "/iteminfo block inventory <position>: gets info about items in an block inventory",
        ]
