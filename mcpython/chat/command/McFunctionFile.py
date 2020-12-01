"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G, logger
import mcpython.ResourceLocator


class McFunctionFile:
    @classmethod
    def from_file(cls, file: str, name: str):
        try:
            return cls(mcpython.ResourceLocator.read(file).decode("utf-8"), name)
        except:
            logger.write_exception("[WARN] failed to load function file {}".format(file))

    def __init__(self, data: str, name: str):
        self.lines = data.split("\n")
        self.name = name

    def execute(self, info=None):
        count = 0
        for line in self.lines:
            if not line.startswith("#"):
                if line.count(" ") + line.count("   ") == len(line): continue
                G.commandparser.parse("/"+line, info.copy())
                count += 1
        G.chat.print_ln("executed {} commands from function {}".format(count, self.name))

