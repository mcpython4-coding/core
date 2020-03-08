"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import ResourceLocator
import globals as G


class McFunctionFile:
    @classmethod
    def from_file(cls, file: str, name: str):
        return cls(ResourceLocator.read(file).decode("utf-8"), name)

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
