"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.chat.command.Command
import mcpython.chat.command.CommandEntry
import mcpython.chat.command.CommandParser
import mcpython.chat.command.Selector
import mcpython.event.Registry
import mcpython.mod.ModMcpython


def register_command(registry, command):
    if issubclass(command, mcpython.chat.command.Command.Command):  # is it an command
        G.commandparser.add_command(command)
    elif issubclass(command, mcpython.chat.command.CommandEntry.CommandEntry):  # or an command entry
        commandregistry.commandentries[command.NAME] = command
    elif issubclass(command, mcpython.chat.command.Selector.Selector):  # or an selector?
        commandregistry.selector.append(command)
    else:
        raise ValueError("can't register object {} to commandhandler".format(command))


commandregistry = mcpython.event.Registry.Registry("command", ["minecraft:command", "minecraft:command_entry",
                                                               "minecraft:selector"],
                                                   injection_function=register_command)
commandregistry.commandentries = {}
commandregistry.selector = []


def load_commands():
    from . import (CommandClear, CommandClone, CommandDataPack, CommandExecute, CommandFill, CommandFunction,
                   CommandGamemode, CommandGameRule, CommandGenerate, CommandGive, CommandItemInfo,
                   CommandKill, CommandLoot, CommandRegistryInfo, CommandReload, CommandReplaceItem,
                   CommandSetblock, CommandSummon, CommandTeleport, CommandTell, CommandXp)

    # register this at the end

    from . import CommandHelp


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:commands", load_commands, info="loading commands")
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:command:entries", mcpython.chat.command.CommandEntry.load)
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:command:selectors", mcpython.chat.command.Selector.load)
