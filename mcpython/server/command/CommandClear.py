"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import ParseBridge, ParseType, ParseMode


@shared.registry
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
        if shared.event_handler.call_cancelable("command:clear", info):
            return  # event for canceling such event

        # when the entity(s) is/are not provided, replace by executing one
        if len(values) == 0:
            values.append([info.entity])

        for entity in values[0]:  # iterate over all entities
            if shared.event_handler.call_cancelable("command:clear:entity", info, entity):
                continue

            if not hasattr(entity, "inventories"):  # has it an inventory?
                info.chat.print_ln("invalid target entity: {}".format(entity))
                continue

            for (
                inventory
            ) in entity.get_inventories():  # iterate over all inventories ...
                inventory.clear()  # ... and clear them

        shared.inventory_handler.moving_slot.get_itemstack().clean()  # make sure that he has nothing in his hand

        shared.event_handler.call(
            "command:clear:end", info
        )  # and call the event that we are done

    @staticmethod
    def get_help() -> list:
        return [
            "/clear [<selector: entities>: default=@s]: clear inventory of given entity(s)"
        ]
