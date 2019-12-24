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
        return self

    def set_attribute(self, name, data):
        if name not in self.table: raise ValueError("Can't write value. Key '{}' not found".format(name))
        if self.table[name][1] is None:
            self.table[name][1] = data
            return data
        else:
            return self.table[name][1]

    def exists_in_table(self, name): return name in self.table and self.table[name][1] is not None

    def get_attribute(self, name):
        return self.table[name][1] if self.exists_in_table(name) else None


FEATURE_FEATURE_TABLE = FeatureTable("features")
FEATURE_FEATURE_TABLE.add_holder("items", "for items").add_holder("blocks", "for blocks").add_holder(
    "materials", "for materials")

ITEMS = FeatureTable("items")
FEATURE_FEATURE_TABLE.set_attribute("items", ITEMS)
BLOCKS = FeatureTable("blocks")
FEATURE_FEATURE_TABLE.set_attribute("blocks", BLOCKS)

MATERIALS = FeatureTable("materials")
FEATURE_FEATURE_TABLE.set_attribute("materials", MATERIALS)

