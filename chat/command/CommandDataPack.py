"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import chat.DataPack


@G.registry
class CommandDatapack(chat.command.Command.Command):
    """
    command /datapack
    """

    NAME = "minecraft:datapack"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "datapack"
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "enable").add_subcommand(SubCommand(
            ParseType.STRING_WITHOUT_QUOTES)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "disable").add_subcommand(SubCommand(
            ParseType.STRING_WITHOUT_QUOTES)))
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "list"))

        # own implementation, will force-delete the assets access of all data-packs, very unstable
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "release"))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if values[0] == "enable":
            for datapack in chat.DataPack.datapackhandler.data_packs:
                if datapack.name == values[1] and chat.DataPack.DataPackStatus.DEACTIVATED:
                    datapack.set_status(chat.DataPack.DataPackStatus.ACTIVATED)
        elif values[0] == "disable":
            for datapack in chat.DataPack.datapackhandler.data_packs:
                if datapack.name == values[1] and chat.DataPack.DataPackStatus.ACTIVATED:
                    datapack.set_status(chat.DataPack.DataPackStatus.DEACTIVATED)
        elif values[0] == "list":
            G.chat.print_ln("count: {}".format(len(chat.DataPack.datapackhandler.data_packs)))
            for datapack in chat.DataPack.datapackhandler.data_packs:
                G.chat.print_ln("- datapack '{}' - status: {}".format(datapack.name, datapack.status.name))
        elif values[0] == "release":
            chat.DataPack.datapackhandler.cleanup()

    @staticmethod
    def get_help() -> list:
        return ["/datapack enable <name>: enables an datapack",
                "/datapack disable <name>: disables an datapack",
                "/datapack list: lists all arrival datapacks with status",
                "/datapack release: unloads all datapacks, decrease memory usage, makes deleting datapacks possible."
                "WARNING: is very unstable"]

