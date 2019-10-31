

class FeatureTable:
    def __init__(self, name):
        self.name = name
        self.table = {}

    def add_holder(self, name, info):
        self.table.setdefault(name, [info, None])

    def set_attribute(self, name, data):
        self.table[name][1] = data


ITEMS = FeatureTable("items")
BLOCKS = FeatureTable("blocks")

MATERIALS = FeatureTable("materials")

