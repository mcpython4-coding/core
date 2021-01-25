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
import mcpython.server.command.CommandEntry
import mcpython.server.command.CommandParser
import mcpython.server.command.Selector
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython


def register_command(registry, command):
    # is it an command
    if issubclass(command, mcpython.server.command.Command.Command):
        shared.command_parser.add_command(command)

    # or an command entry
    elif issubclass(
        command, mcpython.server.command.CommandEntry.CommandEntry
    ):
        command_registry.command_entries[command.NAME] = command

    # or an selector?
    elif issubclass(
        command, mcpython.server.command.Selector.Selector
    ):
        command_registry.selector.append(command)

    else:
        raise ValueError("can't register object '{}' to command handler".format(command))


command_registry = mcpython.common.event.Registry.Registry(
    "minecraft:command",
    ["minecraft:command", "minecraft:command_entry", "minecraft:selector"],
    "stage:commands",
    injection_function=register_command,
)
command_registry.command_entries = {}
command_registry.selector = []


def load_commands():
    from . import (
        CommandClear,
        CommandClone,
        CommandDataPack,
        CommandExecute,
        CommandFill,
        CommandFunction,
        CommandGamemode,
        CommandGameRule,
        CommandGenerate,
        CommandGive,
        CommandItemInfo,
        CommandKill,
        CommandLoot,
        CommandRegistryInfo,
        CommandReload,
        CommandReplaceItem,
        CommandSetblock,
        CommandSummon,
        CommandTeleport,
        CommandTell,
        CommandXp,
        CommandShuffleData,
        CommandBlockInfo,
        CommandRecipeView,
    )

    # register this at the end

    from . import CommandHelp


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:commands", load_commands, info="loading commands"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:command:entries", mcpython.server.command.CommandEntry.load
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:command:selectors", mcpython.server.command.Selector.load
)
