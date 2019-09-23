"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G


class Tag:
    @staticmethod
    def from_data(master, tagname: str, data: dict):
        return Tag(master, tagname, data["values"])

    def __init__(self, master, name: str, entries):
        self.entries = entries
        self.master = master
        self.name = name

    def get_dependencies(self) -> list:
        dep = []
        for entry in self.entries:
            if entry.startswith("#") and entry in self.master.tags:
                dep.append(entry)
        return dep

    def build(self):
        raw = self.entries[:]
        self.entries = []
        for entry in raw:
            if entry.startswith("#"):
                self.entries += self.master.tags[entry].entries
            else:
                self.entries.append(entry)


