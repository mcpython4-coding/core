import typing

from mcpython import logger
from mcpython import shared
import mcpython.server.command.Builder
import mcpython.common.mod.ModMcpython


class CommandExecutionEnvironment:
    def copy(self):
        pass


class CommandParser:
    def __init__(self):
        self.commands: typing.Dict[str, mcpython.server.command.Builder.Command] = {}

    def run(self, string: str, env: CommandExecutionEnvironment):
        node, data = self.parse(string)

        try:
            for func in node.on_execution_callbacks:
                func(env, data)
        except:
            logger.print_exception(f"command parser: during running {string} in {env} using {node}")

    def parse(self, string: str):
        tracker = mcpython.server.command.Builder.CommandExecutionTracker.from_string(string)
        head = tracker.get().removeprefix("/")

        if head not in self.commands:
            logger.println(f"[COMMAND PARSER][ERROR] invalid command {head} ({string})")
            return

        command = self.commands[head]
        try:
            node = command.get_executing_node(tracker)
        except:
            logger.print_exception(f"command parser during parsing /{head} ({string})")
            return

        if node is None:
            logger.println(f"[COMMAND PARSER][ERROR] invalid command syntax {head} ({string})")
            for error in tracker.parsing_errors:
                logger.println("- "+error)
            return

        return node, tracker.collected_values

    def register_command(self, command: mcpython.server.command.Builder.Command):
        self.commands[command.name.removeprefix("/")] = command
        return self


shared.command_parser = CommandParser()


def load_commands():
    from . import CommandSetblock


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:commands", load_commands)

