"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import chat.command.Command


class CommandParser:
    def __init__(self):
        self.commandparsing = {}  # start -> (Command, ParseBridge)

    def add_command(self, command: chat.command.Command):
        parsebridge = chat.command.Command.ParseBridge(command)
        self.commandparsing[parsebridge.main_entry] = (command, parsebridge)

    def parse(self, command: str):
        splitted = command.split(" ")
        pre = splitted[0]
        if pre[1:] in self.commandparsing:
            command, parsebridge = self.commandparsing[pre[1:]]
            values, trace = self._convert_to_values(splitted, parsebridge)
            if values is None: return
            command.parse(values, trace)
        else:
            print("[CHAT][COMMANDPARSER][ERROR] unknown command '{}'".format(pre))

    def _convert_to_values(self, command, parsebridge, index=1) -> tuple:
        # print(command)
        active_entry = parsebridge
        values = []
        array = [parsebridge]
        while len(active_entry.sub_commands) > 0 and index < len(command):
            flag1 = False
            for subcommand in active_entry.sub_commands:
                if not flag1 and subcommand.is_valid(command, index):
                    array.append((subcommand, active_entry.sub_commands.index(subcommand)))
                    active_entry = subcommand
                    index, value = active_entry.parse(command, index)
                    values.append(value)
                    flag1 = True
            if not flag1:
                if all([subcommand.mode == chat.command.Command.ParseMode.OPTIONAL for subcommand in
                        active_entry.sub_commands]):
                    return values, array
                else:
                    print("[CHAT][COMMANDPARSER][ERROR] can't parse command, missing entry at position {}".
                          format(len(array)+1))
                    print("mising one of the following entrys: {}".format([subcommand.type for subcommand in
                                                                           active_entry.sub_commands]))
                    print("gotten values: {}".format(values))
                    return None, array
        return values, array


G.commandparser = CommandParser()

