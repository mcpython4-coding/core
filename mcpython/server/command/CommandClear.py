"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.server.command.Command
from mcpython.server.command.Command import ParseBridge, ParseType, ParseMode


@G.registry
class CommandClear(mcpython.server.command.Command.Command):
    """
    Class for the /clear command

    events:
        - command:clear(CancelAbleEvent, ParsingCommandInfo): called when /clear is executed
        - command:clear:entity(CancelAbleEvent, ParsingCommandInfo, Entity): called for every entity affected by /clear.
            Will cancel /clear only for THIS entity
        - command:clear:finish(ParsingCommandInfo): called by command "/clear" on end of clearing inventory

        removed:
        - command:clear:start & command:clear:end
    """

    NAME = "minecraft:clear"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "clear"
        parsebridge.add_subcommand(ParseType.SELECTOR.set_mode(ParseMode.OPTIONAL))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if G.eventhandler.call_cancelable("command:clear", info):
            return  # event for canceling such event

        # when the entity(s) is/are not provided, replace by executing one
        if len(values) == 0:
            values.append([info.entity])

        for entity in values[0]:  # iterate over all entities
            if G.eventhandler.call_cancelable("command:clear:entity", info, entity):
                continue

            if not hasattr(entity, "inventories"):  # has it an inventory?
                info.chat.print_ln("invalid target entity: {}".format(entity))
                continue

            for (
                inventory
            ) in entity.get_inventories():  # iterate over all inventories ...
                inventory.clear()  # ... and clear them

        G.inventoryhandler.moving_slot.get_itemstack().clean()  # make sure that he has nothing in his hand

        G.eventhandler.call(
            "command:clear:end", info
        )  # and call the event that we are done

    @staticmethod
    def get_help() -> list:
        return [
            "/clear [<selector: entities>: default=@s]: clear inventory of given entity(s)"
        ]
