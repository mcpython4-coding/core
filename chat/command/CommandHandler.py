"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
import chat.command.CommandParser
import chat.command.CommandEntry
import chat.command.Selector
import event.Registry
import mod.ModMcpython


def register_command(registry, command):
    if issubclass(command, chat.command.Command.Command):  # is it an command
        G.commandparser.add_command(command)
    elif issubclass(command, chat.command.CommandEntry.CommandEntry):  # or an command entry
        commandregistry.commandentries[command.NAME] = command
    elif issubclass(command, chat.command.Selector.Selector):  # or an selector?
        commandregistry.selector.append(command)
    else:
        raise ValueError("can't register object {} to commandhandler".format(command))


commandregistry = event.Registry.Registry("command", ["minecraft:command", "minecraft:command_entry",
                                                      "minecraft:selector"],
                                          injection_function=register_command)
commandregistry.commandentries = {}
commandregistry.selector = []


def load_commands():
    from . import (CommandGive, CommandGamemode, CommandExecute, CommandKill, CommandClear, CommandTeleport,
                   CommandReload, CommandGenerate, CommandSetblock, CommandFill, CommandItemInfo, CommandXp,
                   CommandRegistryInfo, CommandFunction, CommandDataPack, CommandClone, CommandTell,
                   CommandReplaceItem, CommandGameRule, CommandLoot, CommandSummon)

    # register this at the end
    from . import CommandHelp


mod.ModMcpython.mcpython.eventbus.subscribe("stage:commands", load_commands, info="loading commands")
mod.ModMcpython.mcpython.eventbus.subscribe("stage:command:entries", chat.command.CommandEntry.load)
mod.ModMcpython.mcpython.eventbus.subscribe("stage:command:selectors", chat.command.Selector.load)

