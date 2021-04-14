"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import typing

from mcpython import logger
from mcpython import shared
import mcpython.server.command.Builder
import mcpython.common.mod.ModMcpython
from mcpython.common.world.AbstractInterface import IDimension


class CommandExecutionEnvironment:
    def __init__(
        self,
        position: typing.Tuple[float, float, float] = None,
        dimension: IDimension = None,
        this=None,
    ):
        self.position = (
            position if position is not None or this is None else this.get_position()
        )
        self.dimension = (
            dimension if dimension is not None or this is None else this.get_dimension()
        )
        self.this = this
        self.chat = None

    def get_dimension(self):
        assert (
            self.dimension is not None
        ), "failed to get dimension; dimension is not set!"
        return self.dimension

    def get_this(self):
        assert self.this is not None, "failed to get 'this'; this is not set"
        return self.this

    def copy(self):
        instance = CommandExecutionEnvironment(self.position, self.dimension, self.this)
        instance.chat = self.chat
        return instance


class CommandParser:
    def __init__(self):
        self.commands: typing.Dict[str, mcpython.server.command.Builder.Command] = {}

    def run(self, string: str, env: CommandExecutionEnvironment):
        parsed = self.parse(string)

        if parsed is None:
            return

        node, data = parsed

        try:
            for func in node.on_execution_callbacks:
                func(env, data)
        except:
            logger.print_exception(
                f"command parser: during running {string} in {env} using {node}"
            )

    def parse(self, string: str):
        tracker = mcpython.server.command.Builder.CommandExecutionTracker.from_string(
            string
        )
        head = tracker.get().removeprefix("/")

        if head not in self.commands:
            logger.println(
                f"[COMMAND PARSER][ERROR] invalid command '/{head}' ({string}): Command base not found"
            )
            return

        command = self.commands[head]
        try:
            node = command.get_executing_node(tracker)
        except:
            logger.print_exception(
                f"command parser during parsing '/{head}' ({string})"
            )
            return

        if node is None:
            logger.println(
                f"[COMMAND PARSER][ERROR] invalid command syntax for command '{head}' ({string}), information "
                "following below on each command node"
            )
            for error in tracker.parsing_errors:
                logger.println("- " + error)
            return

        return node, tracker.collected_values

    def register_command(self, command: mcpython.server.command.Builder.Command):
        self.commands[command.name.removeprefix("/")] = command
        return self


shared.command_parser = CommandParser()


def load_commands():
    from . import (
        CommandSetblock,
        CommandClear,
        CommandGamemode,
        CommandGive,
        CommandKill,
        CommandBlockInfo,
    )


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:commands", load_commands
)
