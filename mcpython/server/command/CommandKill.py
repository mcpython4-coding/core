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
from mcpython.server.command.Command import (
    ParseBridge,
    ParseType,
    ParseMode,
    SubCommand,
)


@shared.registry
class CommandKill(mcpython.server.command.Command.Command):
    """
    class for /kill command
    """

    NAME = "minecraft:kill"

    @staticmethod
    def insert_parse_bridge(parse_bridge: ParseBridge):
        parse_bridge.main_entry = "kill"
        parse_bridge.add_subcommand(
            SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL)
        )

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0:
            values.append([shared.world.get_active_player()])
        for entity in values[0]:
            entity.kill(test_totem=False)  # kill all entities selected

    @staticmethod
    def get_help() -> list:
        return ["/kill [<selector>: default=@s]: kills entity(s)"]
