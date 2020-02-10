"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import ResourceLocator


class BlockConfigEntry:
    def __init__(self, configname):
        self.name = configname
        self.affects = []

    def add_data(self, data):
        self.affects += data

    def contains(self, item): return item in self.affects

    def __contains__(self, item): return self.contains(item)


ENTRYS = {}


for file in ResourceLocator.get_all_entries_special("assets/config/block"):
    name = file.split("/")[-1].split(".")[0]
    if name not in ENTRYS: ENTRYS[name] = BlockConfigEntry(name)
    ENTRYS[name].add_data(ResourceLocator.read(file, mode="json"))

