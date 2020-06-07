"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.chat.command.Command
from mcpython.chat.command.Command import SubCommand, ParseBridge, ParseType, ParseMode


@G.registry
class CommandExecute(mcpython.chat.command.Command.Command):
    """
    class for /execute command
    """

    NAME = "minecraft:execute"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        # missing: align, anchored, facing, in
        execute_as = SubCommand(ParseType.DEFINIED_STRING, "as", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.SELECTOR))
        execute_at = SubCommand(ParseType.DEFINIED_STRING, "at", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.POSITION))
        # missing: blocks, data, score
        execute_if = SubCommand(ParseType.DEFINIED_STRING, "if", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "block").add_subcommand(
                SubCommand(ParseType.POSITION).add_subcommand(ParseType.BLOCKNAME)
            )
        ).add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "entity").add_subcommand(
                SubCommand(ParseType.SELECTOR)
            )
        )
        execute_run = SubCommand(ParseType.DEFINIED_STRING, "run", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.OPEN_END_UNDEFINITED_STRING, min=1)
        )
        execute_unless = SubCommand(ParseType.DEFINIED_STRING, "unless", mode=ParseMode.OPTIONAL)
        execute_unless.sub_commands = execute_if.sub_commands
        sub_commands = [execute_as, execute_at, execute_if, execute_run]
        sub_commands_ends = [execute_as.sub_commands[0], execute_at.sub_commands[0],
                             execute_if.sub_commands[0].sub_commands[0].sub_commands[0],
                             execute_if.sub_commands[1].sub_commands[0],
                             execute_unless.sub_commands[0].sub_commands[0].sub_commands[0],
                             execute_unless.sub_commands[1].sub_commands[0]]
        for subcommand in sub_commands_ends + [parsebridge]:  # every end can be assinged with an new
            subcommand.sub_commands = sub_commands
        parsebridge.main_entry = "execute"

    @staticmethod
    def parse(values: list, modes: list, info):
        CommandExecute._parse_subcommand(0, values[index], values, info)  # execute first entry

    @staticmethod
    def _parse_subcommand(index, command, values, info):
        """
        execute an entry in the parsed command
        :param index: the index to start
        :param command: the parsed active command
        :param values: the values that where parsed
        :param info: the command info which was used
        """

        if command == "as":
            index += 2
            for entity in values[index+1]:
                info.entity = entity
                CommandExecute._parse_subcommand(index, values[index], values, info)
            return
        elif command == "at":
            index += 2
            for position in values[index + 1]:
                info.position = position
                CommandExecute._parse_subcommand(index, values[index], values, info)
            return
        elif command in ["if", "unless"]:
            subcommand: str = values[index+1]
            index += 2
            flag = None
            if subcommand == "block":
                position, name = values[index], values[index+1]
                index += 2
                if position in G.world.world:
                    block = G.world.world[position]
                    flag = block.NAME == G.registry.get_by_name("block").registered_object_map[name].NAME
                else:
                    flag = name in ["air", "minecraft:air", None, 0]
            elif subcommand == "entity":
                selector = values[index]
                index += 1
                flag = len(selector) > 0

            # should we exit?
            if command == "unless" if flag else command == "if": return
        elif command == "run":
            # execute command
            G.commandparser.parse("/"+" ".join(values[index+1]), info=info)
            index += 2

        if len(values) > index:  # have we more commands to parse?
            CommandExecute._parse_subcommand(index, values[index], values, info)

    @staticmethod
    def get_help() -> list:
        return ["/execute \\as <selector>\\at <position>\\if / unless \\block <position> <blockname>\\entity <selector>"
                "\\ \\ run <command>: execute command with given arguments"]
