"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseType, ParseMode, SubCommand, ParseBridge
import gui.ItemStack
import gui.ItemStack


@G.registry
class CommandReplaceItem(chat.command.Command.Command):
    """
    class for /replaceitem command
    """

    NAME = "minecraft:replace_item"

    CANCEL_GIVE = False

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "replaceitem"
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "block").add_subcommand(
            SubCommand(ParseType.POSITION).add_subcommand(SubCommand(ParseType.INT).add_subcommand(
                SubCommand(ParseType.ITEMNAME).add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL))))))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "entity").add_subcommand(
            SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(ParseType.INT).add_subcommand(
                SubCommand(ParseType.ITEMNAME).add_subcommand(SubCommand(ParseType.INT, mode=ParseMode.OPTIONAL))))))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if values[0] == "block":
            block = G.world.get_active_dimension().get_block(values[1])
            if block is not None and type(block) != str:
                if block.get_inventories() == 0:
                    G.chat.print_ln("[ERROR] block does not have any inventory")
                    return
                inventory = block.get_inventories()[0]
                slot_id = values[2]
                if slot_id < 0:
                    G.chat.print_ln("[ERROR] slot id must be greater than 0")
                    return
                if slot_id >= len(inventory.slots):
                    G.chat.print_ln("[ERROR] slot id {} is bigger than slot count {}".format(slot_id,
                                                                                             len(inventory.slots)))
                    return
                slot = inventory.slots[slot_id]
                slot.set_itemstack(gui.ItemStack.ItemStack(values[3], 1 if len(values) == 4 else values[4]))
            else:
                G.chat.print_ln("[ERROR] at position {} is no block".format(values[1]))
        elif values[0] == "entity":
            for entity in values[1]:
                slot_id = values[2]
                if slot_id < 0:
                    G.chat.print_ln("[ERROR] slot id must be greater than 0")
                    return
                if slot_id >= len(entity.inventory_slots):
                    G.chat.print_ln("[ERROR] slot id {} is bigger than slot count {}".format(
                        slot_id, len(entity.inventory_slots)))
                    return
                slot = entity.inventory_slots[slot_id]
                slot.set_itemstack(gui.ItemStack.ItemStack(values[3], 1 if len(values) == 4 else values[4]))

    @staticmethod
    def get_help() -> list:
        return ["/replaceitem block <position> <slot> <item> [<amount>]: sets an slot of an block-inventory",
                "/replaceitem entity <selector> <slot> <item> [<amount>]: sets an slot in an entity-inventory"]

