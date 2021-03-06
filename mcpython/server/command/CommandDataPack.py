"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.common.DataPack
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    Node,
)


@shared.registry
class CommandDatapack(mcpython.server.command.Command.Command):
    """
    Class holding the /datapack command
    """

    NAME = "minecraft:datapack"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "datapack"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "enable").add_node(
                Node(CommandArgumentType.STRING_WITHOUT_QUOTES)
            )
        )
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "disable").add_node(
                Node(CommandArgumentType.STRING_WITHOUT_QUOTES)
            )
        )
        command_syntax_holder.add_node(Node(CommandArgumentType.DEFINED_STRING, "list"))

        # own implementation, will force-delete the assets access of all data-packs, very unstable
        # todo: remove
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "release")
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        if values[0] == "enable":
            for datapack in mcpython.common.DataPack.datapack_handler.loaded_data_packs:
                if (
                    datapack.name == values[1]
                    and mcpython.common.DataPack.DataPackStatus.DEACTIVATED
                ):
                    datapack.set_status(
                        mcpython.common.DataPack.DataPackStatus.ACTIVATED
                    )

        elif values[0] == "disable":
            for datapack in mcpython.common.DataPack.datapack_handler.loaded_data_packs:
                if (
                    datapack.name == values[1]
                    and mcpython.common.DataPack.DataPackStatus.ACTIVATED
                ):
                    datapack.set_status(
                        mcpython.common.DataPack.DataPackStatus.DEACTIVATED
                    )

        elif values[0] == "list":
            info.chat.print_ln(
                "count: {}".format(
                    len(mcpython.common.DataPack.datapack_handler.loaded_data_packs)
                )
            )
            for datapack in mcpython.common.DataPack.datapack_handler.loaded_data_packs:
                info.chat.print_ln(
                    "- datapack '{}' - status: {}".format(
                        datapack.name, datapack.status.name
                    )
                )

        elif values[0] == "release":
            shared.event_handler.call("command:datapack:release", info)
            mcpython.common.DataPack.datapack_handler.cleanup()

        else:
            info.chat.print_ln("failed to execute command. invalid syntax")

    @staticmethod
    def get_help() -> list:
        return [
            "/datapack enable <name>: enables an datapack with name <name>",
            "/datapack disable <name>: disables an datapack with name <name>",
            "/datapack list: lists all arrival datapacks with status",
            "/datapack release: unloads all datapacks, decrease memory usage, makes deleting datapacks possible.",
        ]
