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
import mcpython.common.DataPack


class CommandExecutionEnvironment:
    def __init__(
        self,
        position: typing.Tuple[float, float, float] = None,
        dimension: IDimension = None,
        this=None,
    ):
        self.position = position
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

    def with_dimension(self, dimension):
        if isinstance(dimension, str):
            self.dimension = self.dimension.get_world().get_dimension_by_name(dimension)
        else:
            self.dimension = dimension
        return self

    def get_position(self):
        assert (
            self.position is not None or self.this is not None
        ), "position cannot be got"
        return self.position if self.position is not None else self.this.get_position()

    def with_position(self, position):
        self.position = position
        return self

    def get_this(self):
        assert self.this is not None, "failed to get 'this'; this is not set"
        return self.this

    def with_this(self, this):
        self.this = this
        return self

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
            node.run(env, data)
        except:
            logger.print_exception(
                f"command parser: during running {string} in {env} using {node}"
            )

    def run_function(self, name: str, info=None):
        # todo: move here
        mcpython.common.DataPack.datapack_handler.try_call_function(name, info)

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
        """
        Helper method for registering a command into the system
        :param command: the command instance
        """

        self.commands[command.name.removeprefix("/")] = command

        for alias in command.additional_names:
            instance = mcpython.server.command.Builder.Command(alias)
            instance.following_nodes = (
                command.following_nodes
            )  # todo: additional meta data
            self.register_command(instance)

        return self


shared.command_parser = CommandParser()


def load_commands():
    # This is the deal, we import & register here, so others can safely import our classes without worrying about
    # flooding the registry in the wrong moment
    # And it also resolves errors during dynamic reload / cross process loading
    # todo: use deferred registering
    # todo: dynamic registering based on module list, by calling register_command() on the given attr of the module
    from . import (
        CommandSetblock,
        CommandClear,
        CommandGamemode,
        CommandGive,
        CommandKill,
        CommandInfo,
        CommandReload,
        CommandWorldGenerationDebug,
        CommandClone,
        CommandFill,
        CommandFunction,
        CommandData,
        CommandGenerate,
        CommandGamerule,
        CommandTell,
        CommandXp,
        CommandExecute,
        CommandDatapack,
        CommandSummon,
        CommandTeleport,
    )

    handler: CommandParser = shared.command_parser

    handler.register_command(CommandSetblock.setblock)
    handler.register_command(CommandClear.clear)
    handler.register_command(CommandGamemode.gamemode)
    handler.register_command(CommandGive.give)
    handler.register_command(CommandKill.kill)
    handler.register_command(CommandInfo.info)
    handler.register_command(CommandReload.reload)
    handler.register_command(CommandWorldGenerationDebug.worldgendebug)
    handler.register_command(CommandClone.clone)
    handler.register_command(CommandFill.fill)
    handler.register_command(CommandFunction.function)
    handler.register_command(CommandData.data)
    handler.register_command(CommandGenerate.generate)
    handler.register_command(CommandGamerule.gamerule)
    handler.register_command(CommandTell.tell)
    handler.register_command(CommandXp.xp)
    handler.register_command(CommandExecute.execute)
    handler.register_command(CommandDatapack.datapack)
    handler.register_command(CommandSummon.summon)
    handler.register_command(CommandTeleport.teleport)


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:commands", load_commands
)
