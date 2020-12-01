"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
import mcpython.client.chat.command.Command
from mcpython.client.chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand


@G.registry
class CommandKill(mcpython.client.chat.command.Command.Command):
    """
    class for /kill command
    """

    NAME = "minecraft:kill"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "kill"
        parsebridge.add_subcommand(SubCommand(ParseType.SELECTOR, mode=ParseMode.OPTIONAL))

    @staticmethod
    def parse(values: list, modes: list, info):
        if len(values) == 0: values.append([G.world.get_active_player()])
        for entity in values[0]:
            entity.kill(test_totem=False)  # kill all entities selected

    @staticmethod
    def get_help() -> list:
        return ["/kill [<selector>: default=@s]: kills entity(s)"]

