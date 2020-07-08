"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import logger
import mcpython.chat.command.Command
from mcpython.chat.command.Command import ParseBridge, ParseType, SubCommand


@G.registry
class CommandLoot(mcpython.chat.command.Command.Command):
    """
    command /loot
    """

    NAME = "minecraft:loot"

    CANCEL_CLEAR = False  # cancel the clear-execute

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "loot"
        end1 = SubCommand(ParseType.DEFINIED_STRING, "loot").add_subcommand(SubCommand(ParseType.STRING_WITHOUT_QUOTES))
        end2 = SubCommand(ParseType.DEFINIED_STRING, "mine").add_subcommand(SubCommand(ParseType.POSITION))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "give").add_subcommand(SubCommand(
            ParseType.SELECTOR).add_subcommand(end1).add_subcommand(end2)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "insert").add_subcommand(SubCommand(
            ParseType.POSITION).add_subcommand(end1).add_subcommand(end2)))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if values[0] == "give":
            for entity in values[1]:
                if values[2] == "loot":
                    entity.pick_up(G.loottablehandler.roll(values[3], player=entity))
                elif values[2] == "mine":
                    block = entity.dimension.get_block(values[3])
                    if block is None or type(block) == str:
                        logger.println("[CHAT][ERROR] position {} does NOT contain any block".format(values[3]))
                        return
                    entity.pick_up(G.loottablehandler.get_drop_for_block(block, entity))
        elif values[0] == "insert":
            block = G.world.get_active_dimension().get_block(values[1])
            if block is None or type(block) == str:
                logger.println("[CHAT][ERROR] position {} contains NO block".format(values[1]))
                return
            if len(block.get_inventories()) == 0:
                logger.println("[CHAT][ERROR] position {} has no inventory".format(values[1]))
            inventory = block.get_inventories()[0]
            if values[2] == "loot":
                inventory.insert_items(G.loottablehandler.roll(values[3], player=entity))
            elif values[2] == "mine":
                blockb = G.world.get_active_dimension().get_block(values[3])
                if blockb is None or type(blockb) == str:
                    logger.println("[CHAT][ERROR] position {} does NOT contain any block".format(values[3]))
                    return
                inventory.insert_items(G.loottablehandler.get_drop_for_block(block, info.entity))

    @staticmethod
    def get_help() -> list:
        return ["/loot <target> <source>: rolls the loot table from source (may be 'loot <loot table id>' or "
                "'mine <position> [<item>|mainhand|offhand]) and inserts it into target (may be 'give <selector>' or "
                "insert <position>)"]

