"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandTeleport(chat.command.Command.Command):
    """
    class for /teleport command
    """

    NAME = "minecraft:teleport"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["tp", "teleport"]  # both are valid
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(ParseType.SELECTOR)).
                                   add_subcommand(SubCommand(ParseType.POSITION))).\
            add_subcommand(SubCommand(ParseType.POSITION))

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][0] == 0:  # tp [selector]
            if modes[2][0] == 0:  # tp [selector] [selector]
                for entity in values[0]:
                    entity.position = tuple(values[1][0].position)
            else:  # tp [selector] [position]
                for entity in values[0]:
                    entity.position = tuple(values[1][0])
        else:  # tp [position]
            G.world.get_active_player().position = tuple(values[0])

    @staticmethod
    def get_help() -> list:
        return ["/tp <selector> <position>: teleport given entity(s) to position",
                "/tp <position>: teleport executer to position",
                "/teleport <selector> <position>: teleport given entity(s) to position",
                "/teleport <position>: teleport executer to position"]

