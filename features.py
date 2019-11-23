"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""


class FeatureTable:
    def __init__(self, name):
        self.name = name
        self.table = {}

    def add_holder(self, name, info):
        self.table.setdefault(name, [info, None])

    def set_attribute(self, name, data):
        if self.table[name][1] is None:
            self.table[name][1] = data
            return data
        else:
            return self.table[name][1]


ITEMS = FeatureTable("items")
BLOCKS = FeatureTable("blocks")

MATERIALS = FeatureTable("materials")

