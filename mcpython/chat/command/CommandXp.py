"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.chat.command.Command
from mcpython.chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandXp(mcpython.chat.command.Command.Command):
    """
    command /xp
    """

    NAME = "minecraft:xp"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = ["xp", "experience"]
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "add").add_subcommand(
            SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(ParseType.INT).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "points", mode=ParseMode.OPTIONAL)
            ).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "levels", mode=ParseMode.OPTIONAL)
            ))
        )).add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "set").add_subcommand(
            SubCommand(ParseType.SELECTOR).add_subcommand(SubCommand(ParseType.INT).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "points", mode=ParseMode.OPTIONAL)
            ).add_subcommand(
                SubCommand(ParseType.DEFINIED_STRING, "levels", mode=ParseMode.OPTIONAL)
            ))
        ))

    @staticmethod
    def parse(values: list, modes: list, info):
        if modes[1][1] in [0, 1]:
            if modes[1][1] == 1:
                G.world.get_active_player().xp = 0
                G.world.get_active_player().xp_level = 0
            if len(modes) == 4 or modes[4][1] == 0:  # points
                for player in values[1]:
                    player.add_xp(values[2])
            elif modes[4][1] == 1:  # levels
                for player in values[1]:
                    player.add_xp_level(values[2])

    @staticmethod
    def get_help() -> list:
        return ["/xp add <selector> <level> [points|levels]: add xp to entity",
                "/xp set <selector> <level> [points|levels]: set xp level of entity"]

