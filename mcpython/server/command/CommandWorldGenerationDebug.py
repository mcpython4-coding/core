"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import CommandSyntaxHolder
import mcpython.util.math
from mcpython.server.command.Command import (
    CommandSyntaxHolder,
    CommandArgumentType,
    CommandArgumentMode,
    Node,
)


@shared.registry
class CommandWorldGenDebug(mcpython.server.command.Command.Command):
    """
    Class for the /worldgendebug command
    """

    NAME = "minecraft:world_gen_debug"

    @staticmethod
    def insert_command_syntax_holder(command_syntax_holder: CommandSyntaxHolder):
        command_syntax_holder.main_entry = "worldgendebug"
        command_syntax_holder.add_node(
            Node(CommandArgumentType.DEFINED_STRING, "info")
        ).add_node(
            Node(CommandArgumentType.DEFINED_STRING, "ping")
        )

    @classmethod
    def parse(cls, values: list, modes: list, info):
        remote_helper = shared.world.world_generation_process
        if values[0] == "info":
            # -1 because we (the query task) are currently also running
            print(remote_helper.get_worker_count())

        elif values[0] == "ping":
            def ping(context):
                print("ping")
                context.get_helper().run_on_main(lambda _: print("pong"))

            remote_helper.run_on_process(ping)

    @staticmethod
    def get_help() -> list:
        return [
            "/worldgendebug info: prints general information about world gen",
            "/worldgendebug ping: pings the world generation process. If everything is fine, prints 'ping' and 'pong'"
        ]
