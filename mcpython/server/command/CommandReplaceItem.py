"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.server.command.Command
import mcpython.common.container.ItemStack
from mcpython.server.command.Command import (
    CommandArgumentType,
    CommandArgumentMode,
    Node,
    CommandSyntaxHolder,
)


@shared.registry
class CommandReplaceItem(mcpython.server.command.Command.Command):
    """
    class for /replaceitem command
    """

    NAME = "minecraft:replace_item"

    CANCEL_GIVE = False

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "replaceitem"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "block").add_node(
                Node(CommandArgumentType.POSITION).add_node(
                    Node(CommandArgumentType.INT).add_node(
                        Node(CommandArgumentType.ITEM_NAME).add_node(
                            Node(
                                CommandArgumentType.INT,
                                mode=CommandArgumentMode.OPTIONAL,
                            )
                        )
                    )
                )
            )
        )
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "entity").add_node(
                Node(CommandArgumentType.SELECTOR).add_node(
                    Node(CommandArgumentType.INT).add_node(
                        Node(CommandArgumentType.ITEM_NAME).add_node(
                            Node(
                                CommandArgumentType.INT,
                                mode=CommandArgumentMode.OPTIONAL,
                            )
                        )
                    )
                )
            )
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if values[0] == "block":
            block = info.entity.dimension.get_block(values[1])
            if block is not None and type(block) != str:
                if len(block.get_inventories()) == 0:
                    info.chat.print_ln("[ERROR] block does not have any inventory")
                    return

                inventory = block.get_inventories()[0]
                slot_id = values[2]

                if slot_id < 0:
                    info.chat.print_ln("[ERROR] slot id must be greater than 0")
                    return

                if slot_id >= len(inventory.slots):
                    info.chat.print_ln(
                        "[ERROR] slot id {} is bigger than slot count {}".format(
                            slot_id, len(inventory.slots)
                        )
                    )
                    return

                slot = inventory.slots[slot_id]
                slot.set_itemstack(
                    mcpython.common.container.ItemStack.ItemStack(
                        values[3], 1 if len(values) == 4 else values[4]
                    )
                )

            else:
                info.chat.print_ln(
                    "[ERROR] at position {} is no block".format(values[1])
                )

        elif values[0] == "entity":
            for entity in values[1]:
                slot_id = values[2]
                if slot_id < 0:
                    info.chat.print_ln("[ERROR] slot id must be greater than 0")
                    return

                if slot_id >= len(entity.inventory_slots):
                    info.chat.print_ln(
                        "[ERROR] slot id {} is bigger than slot count {}".format(
                            slot_id, len(entity.inventory_slots)
                        )
                    )
                    return

                slot = entity.inventory_slots[slot_id]
                slot.set_itemstack(
                    mcpython.common.container.ItemStack.ItemStack(
                        values[3], 1 if len(values) == 4 else values[4]
                    )
                )

    @staticmethod
    def get_help() -> list:
        return [
            "/replaceitem block <position> <slot> <item> [<amount>]: sets an slot of an block-inventory",
            "/replaceitem entity <selector> <slot> <item> [<amount>]: sets an slot in an entity-inventory",
        ]
