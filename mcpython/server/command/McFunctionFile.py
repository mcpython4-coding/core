"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.ResourceLoader


class McFunctionFile:
    @classmethod
    def from_file(cls, file: str, name: str):
        try:
            return cls(mcpython.ResourceLoader.read_raw(file).decode("utf-8"), name)
        except:
            logger.print_exception(
                "[WARN] failed to load function file {}".format(file)
            )

    def __init__(self, data: str, name: str):
        self.lines = data.split("\n")
        self.name = name
        # todo: pre-parse data

    def execute(self, info=None):
        count = 0
        for line in self.lines:
            if not line.startswith("#"):
                if line.count(" ") + line.count("   ") == len(line):
                    continue

                shared.command_parser.parse(
                    "/" + line, info.copy(include_variables=False)
                )
                count += 1
        shared.chat.print_ln(
            "executed {} commands from function {}".format(count, self.name)
        )
