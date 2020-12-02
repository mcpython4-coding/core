"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.client.chat.DataPack
import mcpython.server.command.Command
from mcpython.server.command.Command import ParseBridge, ParseType, SubCommand


@G.registry
class CommandDatapack(mcpython.server.command.Command.Command):
    """
    Class holding the /datapack command
    """

    NAME = "minecraft:datapack"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "datapack"
        parsebridge.add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "enable").add_subcommand(
                SubCommand(ParseType.STRING_WITHOUT_QUOTES)
            )
        )
        parsebridge.add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "disable").add_subcommand(
                SubCommand(ParseType.STRING_WITHOUT_QUOTES)
            )
        )
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "list"))

        # own implementation, will force-delete the assets access of all data-packs, very unstable
        parsebridge.add_subcommand(SubCommand(ParseType.DEFINIED_STRING, "release"))

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if values[0] == "enable":
            for datapack in mcpython.client.chat.DataPack.datapackhandler.data_packs:
                if (
                    datapack.name == values[1]
                    and mcpython.client.chat.DataPack.DataPackStatus.DEACTIVATED
                ):
                    datapack.set_status(
                        mcpython.client.chat.DataPack.DataPackStatus.ACTIVATED
                    )

        elif values[0] == "disable":
            for datapack in mcpython.client.chat.DataPack.datapackhandler.data_packs:
                if (
                    datapack.name == values[1]
                    and mcpython.client.chat.DataPack.DataPackStatus.ACTIVATED
                ):
                    datapack.set_status(
                        mcpython.client.chat.DataPack.DataPackStatus.DEACTIVATED
                    )

        elif values[0] == "list":
            info.chat.print_ln(
                "count: {}".format(
                    len(mcpython.client.chat.DataPack.datapackhandler.data_packs)
                )
            )
            for datapack in mcpython.client.chat.DataPack.datapackhandler.data_packs:
                info.chat.print_ln(
                    "- datapack '{}' - status: {}".format(
                        datapack.name, datapack.status.name
                    )
                )

        elif values[0] == "release":
            G.eventhandler.call("command:datapack:release", info)
            mcpython.client.chat.DataPack.datapackhandler.cleanup()
        else:
            G.chat.print_ln("failed to execute command. invalid syntax")

    @staticmethod
    def get_help() -> list:
        return [
            "/datapack enable <name>: enables an datapack with name <name>",
            "/datapack disable <name>: disables an datapack with name <name>",
            "/datapack list: lists all arrival datapacks with status",
            "/datapack release: unloads all datapacks, decrease memory usage, makes deleting datapacks possible.",
        ]
