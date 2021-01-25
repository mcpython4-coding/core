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
from mcpython.server.command.Command import ParseBridge, ParseType, SubCommand


@shared.registry
class CommandLoot(mcpython.server.command.Command.Command):
    """
    command /loot
    """

    NAME = "minecraft:loot"

    CANCEL_CLEAR = False  # cancel the clear-execute

    @staticmethod
    def insert_parse_bridge(parse_bridge: ParseBridge):
        parse_bridge.main_entry = "loot"
        end1 = SubCommand(ParseType.DEFINED_STRING, "loot").add_subcommand(
            SubCommand(ParseType.STRING_WITHOUT_QUOTES)
        )
        end2 = SubCommand(ParseType.DEFINED_STRING, "mine").add_subcommand(
            SubCommand(ParseType.POSITION)
        )
        parse_bridge.add_subcommand(
            SubCommand(ParseType.DEFINED_STRING, "give").add_subcommand(
                SubCommand(ParseType.SELECTOR).add_subcommand(end1).add_subcommand(end2)
            )
        )
        parse_bridge.add_subcommand(
            SubCommand(ParseType.DEFINED_STRING, "insert").add_subcommand(
                SubCommand(ParseType.POSITION).add_subcommand(end1).add_subcommand(end2)
            )
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if values[0] == "give":
            for entity in values[1]:
                if values[2] == "loot":
                    entity.pick_up_item(
                        shared.loot_table_handler.roll(values[3], player=entity)
                    )

                elif values[2] == "mine":
                    block = entity.dimension.get_block(values[3])
                    if block is None or type(block) == str:
                        logger.println(
                            "[CHAT][ERROR] position {} does NOT contain any block".format(
                                values[3]
                            )
                        )
                        return
                    entity.pick_up_item(
                        shared.loot_table_handler.get_drop_for_block(block, entity)
                    )

        elif values[0] == "insert":
            block = info.entity.dimension.get_block(values[1])
            if block is None or type(block) == str:
                logger.println(
                    "[CHAT][ERROR] position {} contains NO block".format(values[1])
                )
                return
            if len(block.get_inventories()) == 0:
                logger.println(
                    "[CHAT][ERROR] position {} has no inventory".format(values[1])
                )
            inventory = block.get_inventories()[0]

            if values[2] == "loot":
                inventory.insert_items(
                    shared.loot_table_handler.roll(values[3], player=info.entity)
                )

            elif values[2] == "mine":
                block_instance = info.entity.dimension.get_block(values[3])
                if block_instance is None or type(block_instance) == str:
                    logger.println(
                        "[CHAT][ERROR] position {} does NOT contain any block".format(
                            values[3]
                        )
                    )
                    return
                inventory.insert_items(
                    shared.loot_table_handler.get_drop_for_block(block, info.entity)
                )

    @staticmethod
    def get_help() -> list:
        return [
            "/loot <target> <source>: rolls the loot table from source (may be 'loot <loot table id>' or "
            "'mine <position> [<item>|mainhand|offhand]) and inserts it into target (may be 'give <selector>' or "
            "insert <position>)"
        ]
