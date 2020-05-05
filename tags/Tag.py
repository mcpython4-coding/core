"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mod.ModMcpython
import logger


class Tag:
    @staticmethod
    def from_data(master, tagname: str, data: dict):
        return Tag(master, tagname, data["values"])

    def __init__(self, master, name: str, entries):
        self.entries = entries
        self.master = master
        self.name = name
        self.load_tries = 0

    def get_dependencies(self) -> list:
        dep = []
        for entry in self.entries:
            if entry.startswith("#") and entry in self.master.tags:
                dep.append(entry)
        return dep

    def build(self):
        raw = self.entries[:]
        old_entries = self.entries
        self.entries = []
        for entry in raw:
            if entry.startswith("#"):
                if entry not in self.master.tags:
                    if self.load_tries > 4:
                        logger.println("[TAG][FATAL] failed to load tag {} as tag {} was not found".format(self.name, entry))
                        self.load_tries = 0
                        old_entries.remove(entry)
                        continue
                    self.entries = old_entries
                    mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:load", self.build)
                    self.load_tries += 1
                    return
                self.entries += self.master.tags[entry].entries
            else:
                self.entries.append(entry)


