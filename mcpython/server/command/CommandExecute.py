"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import itertools
import typing

from mcpython import shared
import mcpython.server.command.Command
from mcpython.server.command.Command import (
    Node,
    CommandSyntaxHolder,
    CommandArgumentType,
    CommandArgumentMode,
)


@shared.registry
class CommandExecute(mcpython.server.command.Command.Command):
    """
    Class for /execute command
    """

    EXECUTE_NODES = {
        "as": Node(
            CommandArgumentType.DEFINED_STRING, "as", mode=CommandArgumentMode.OPTIONAL
        ).add_node(Node(CommandArgumentType.SELECTOR)),
        "at": Node(
            CommandArgumentType.DEFINED_STRING, "at", mode=CommandArgumentMode.OPTIONAL
        ).add_node(Node(CommandArgumentType.POSITION)),
        "in": Node(
            CommandArgumentType.DEFINED_STRING, "in", mode=CommandArgumentMode.OPTIONAL
        ).add_node(Node(CommandArgumentType.DIMENSION_NAME)),
        "if": Node(
            CommandArgumentType.DEFINED_STRING,
            "if",
            mode=CommandArgumentMode.OPTIONAL,
        )
        .add_node(
            Node(CommandArgumentType.DEFINED_STRING, "block").add_node(
                Node(CommandArgumentType.POSITION).add_node(
                    CommandArgumentType.BLOCK_NAME
                )
            )
        )
        .add_node(
            Node(CommandArgumentType.DEFINED_STRING, "entity").add_node(
                Node(CommandArgumentType.SELECTOR)
            )
        )
        .add_node(
            Node(CommandArgumentType.DEFINED_STRING, "var")
            .add_node(
                Node(CommandArgumentType.DEFINED_STRING, "defined").add_node(
                    Node(CommandArgumentType.STRING_WITHOUT_QUOTES)
                )
            )
            .add_node(
                Node(CommandArgumentType.DEFINED_STRING, "compare").add_node(
                    CommandArgumentType.DEFINED_STRING.add_node(
                        Node(CommandArgumentType.DEFINED_STRING, "==").add_node(
                            CommandArgumentType.STRING_WITHOUT_QUOTES
                        )
                    )
                    .add_node(
                        Node(CommandArgumentType.DEFINED_STRING, "!=").add_node(
                            CommandArgumentType.STRING_WITHOUT_QUOTES
                        )
                    )
                    .add_node(
                        Node(CommandArgumentType.DEFINED_STRING, ">").add_node(
                            CommandArgumentType.STRING_WITHOUT_QUOTES
                        )
                    )
                    .add_node(
                        Node(CommandArgumentType.DEFINED_STRING, ">=").add_node(
                            CommandArgumentType.STRING_WITHOUT_QUOTES
                        )
                    )
                    .add_node(
                        Node(CommandArgumentType.DEFINED_STRING, "<").add_node(
                            CommandArgumentType.STRING_WITHOUT_QUOTES
                        )
                    )
                    .add_node(
                        Node(CommandArgumentType.DEFINED_STRING, "<=").add_node(
                            CommandArgumentType.STRING_WITHOUT_QUOTES
                        )
                    )
                )
            )
        ),

        # sub-nodes are copied from if-condition during command init, and are shared
        "unless": Node(
            CommandArgumentType.DEFINED_STRING,
            "unless",
            mode=CommandArgumentMode.OPTIONAL,
        ),
    }

    EXECUTE_END_NODES = [
        Node(
            CommandArgumentType.DEFINED_STRING, "run", mode=CommandArgumentMode.OPTIONAL
        ).add_node(Node(CommandArgumentType.OPEN_END_UNDEFINED_STRING, min=1))
    ]

    SPECIAL_NODE_PARSING = {}

    NAME = "minecraft:execute"

    @classmethod
    def insert_command_syntax_holder(cls, command_syntax_holder: CommandSyntaxHolder):
        # missing: align, anchored, facing
        # missing: blocks, data, score

        command_syntax_holder.main_entry = "execute"
        followed = []

        old = cls.EXECUTE_NODES["unless"].nodes
        cls.EXECUTE_NODES["unless"].nodes = cls.EXECUTE_NODES["if"].nodes
        cls.EXECUTE_NODES["unless"].nodes.extend(old)

        for node in cls.EXECUTE_NODES.values():
            followed.extend(node.get_node_ends())

        for node in cls.EXECUTE_NODES.values():
            command_syntax_holder.add_node(node)

        for node in followed:
            for entry in itertools.chain(
                cls.EXECUTE_NODES.values(), cls.EXECUTE_END_NODES
            ):
                node.add_node(entry)

    @staticmethod
    def parse(values: list, modes: list, info):
        CommandExecute._parse_subcommand(
            0, values[0], values, info
        )  # execute first entry

    @classmethod
    def _parse_subcommand(cls, index: int, command: str, values: typing.List, info):
        """
        Execute an entry in the parsed command
        :param index: the index to start
        :param command: the parsed active command
        :param values: the values that where parsed
        :param info: the command info which was used
        Mods adding custom entries should use the SPECIAL_NODE_PARSING extension point for parsing their entries
        """

        if command == "as":
            index += 2
            for entity in values[index + 1]:
                info.entity = entity
                CommandExecute._parse_subcommand(index, values[index], values, info)
            return

        elif command == "at":
            index += 2
            for position in values[index - 1]:
                info.position = position
                CommandExecute._parse_subcommand(index, values[index], values, info)
            return

        elif command in ["if", "unless"]:
            subcommand: str = values[index + 1]
            index += 2
            flag = None

            if subcommand == "block":
                position, name = values[index], values[index + 1]
                index += 2
                if position in shared.world.world:
                    block = shared.world.world[position]
                    flag = (
                        block.NAME
                        == shared.registry.get_by_name("minecraft:block")[name].NAME
                    )
                else:
                    flag = name in ["air", "minecraft:air", None, 0]

            elif subcommand == "entity":
                selector = values[index]
                index += 1
                flag = len(selector) > 0

            elif subcommand == "var":
                if values[index] == "defined":
                    flag = (
                        values[index + 1].removeprefix("<").removesuffix(">")
                        in info.local_variable_stack
                    )
                    index += 2

                elif values[index] == "compare":
                    a, op, b = values[index + 1 : index + 5]
                    # todo: make more safe
                    flag = eval(
                        "{} {} {}".format(
                            info.local_variable_stack[a[1:-1]]
                            if a.startswith("<")
                            else a,
                            op,
                            info.local_variable_stack[b[1:-1]]
                            if b.startswith("<")
                            else b,
                        )
                    )
                    index += 4

            # should we exit?
            if command == "unless" if flag else command == "if":
                return

        elif command == "in":
            info.dimension = shared.world.get_dimension_by_name(
                values[index + 1]
            ).get_id()
            index += 2
            CommandExecute._parse_subcommand(index, values[index], values, info)
            return

        elif command == "run":
            # execute command
            shared.command_parser.parse("/" + " ".join(values[index + 1]), info=info)
            index += 2

        elif command in cls.SPECIAL_NODE_PARSING:
            cls.SPECIAL_NODE_PARSING[command](index, command, values, info)

        if len(values) > index:  # have we more commands to parse?
            CommandExecute._parse_subcommand(index, values[index], values, info)

    @staticmethod
    def get_help() -> list:
        # todo: build dynamically
        return [
            "/execute \\as <selector>\\at <position>\\in <dimension id>\\if / unless \\block <position> <blockname>\\entity <selector>"
            "\\ \\ run <command>: execute command with given arguments"
        ]
