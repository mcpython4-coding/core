"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.server.command.Command
import mcpython.server.command.CommandEntry
import mcpython.server.command.CommandParser
import mcpython.server.command.Selector
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython


def register_command(registry, command):
    if issubclass(command, mcpython.server.command.Command.Command):  # is it an command
        G.commandparser.add_command(command)
    elif issubclass(
        command, mcpython.server.command.CommandEntry.CommandEntry
    ):  # or an command entry
        commandregistry.command_entries[command.NAME] = command
    elif issubclass(
        command, mcpython.server.command.Selector.Selector
    ):  # or an selector?
        commandregistry.selector.append(command)
    else:
        raise ValueError("can't register object {} to commandhandler".format(command))


commandregistry = mcpython.common.event.Registry.Registry(
    "command",
    ["minecraft:command", "minecraft:command_entry", "minecraft:selector"],
    "stage:commands",
    injection_function=register_command,
)
commandregistry.command_entries = {}
commandregistry.selector = []


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
