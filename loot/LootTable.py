import ResourceLocator
import enum
import random
import gui.ItemStack
import globals as G


class LootTableTypes(enum.Enum):
    UNSET = 0
    EMPTY = 1
    ENTITY = 2
    BLOCK = 3
    CHEST = 4
    FISHING = 5
    GIFT = 6
    ADVANCEMENT_REWARD = 7
    GENERIC = 8


class LootTablePoolEntryType(enum.Enum):
    UNSET = 0
    ITEM = 1
    TAG = 2
    LOOT_TABLE = 3
    GROUP = 4
    ALTERNATIVES = 5
    SEQUENCE = 6
    DYNAMIC = 7
    EMPTY = 8


class LootTableHandler:
    def __init__(self):
        self.loot_tables = {}

    def __getitem__(self, item):
        return self.loot_tables[item]

    def roll(self, name: str, *args, **kwargs) -> list:
        if name.count(":") == 0:
            name = "minecraft:" + name
        return self[name].roll(*args, **kwargs)


handler = LootTableHandler()


class LootTablePoolEntry:
    @classmethod
    def from_data(cls, pool, data: dict):
        obj = cls(entry_type=LootTablePoolEntryType[data["type"]])
        obj.pool = pool
        if "conditions" in data:
            obj.conditions = [cond for cond in data["conditions"]]
        if "functions" in data:
            obj.functions = [func for func in data["functions"]]
        if "name" in data:
            obj.name = data["name"]
        if "children" in data:
            obj.children = [cls.from_data(pool, d) for d in data["children"]]
        if "expand" in data:
            obj.expand = data["expand"]
        if "weight" in data:
            obj.weight = data["weight"]
        if "quality" in data:
            obj.quality = data["quality"]
        return obj

    def __init__(self, entry_type=LootTablePoolEntryType.UNSET):
        self.pool = None
        self.entry_type = entry_type
        self.conditions = []
        self.name = None
        self.children = [None]
        self.expand = False
        self.functions = []
        self.weight = 1
        self.quality = 0

    def roll(self, *args, **kwargs):
        if self.entry_type == LootTablePoolEntryType.UNSET: raise ValueError("type not set")
        if not all([cond.check(self, *args, **kwargs) for cond in self.conditions]): return None
        items = []
        if self.entry_type == LootTablePoolEntryType.ITEM:
            items.append(gui.ItemStack.ItemStack(self.name))
        elif self.entry_type == LootTablePoolEntryType.TAG:
            if self.expand:
                items.append(gui.ItemStack.ItemStack(random.choice(G.taghandler.get_tag_for(self.name, "items"))))
            else:
                items += [gui.ItemStack.ItemStack(name) for name in G.taghandler.get_tag_for(self.name, "items")]
        elif self.entry_type == LootTablePoolEntryType.LOOT_TABLE:
            items += handler.roll(self.name, *args, **kwargs)
        elif self.entry_type == LootTablePoolEntryType.GROUP:
            [items.extend(e.roll(*args, **kwargs)) for e in self.children]
        elif self.entry_type == LootTablePoolEntryType.ALTERNATIVES:
            for entry in self.children:
                item = entry.roll(*args, **kwargs)
                if item is None: continue
                items += item
                break
        elif self.entry_type == LootTablePoolEntryType.SEQUENCE:
            for entry in self.children:
                item = entry.roll(*args, **kwargs)
                if item is None: break
                items += item
        elif self.entry_type == LootTablePoolEntryType.DYNAMIC:
            raise NotImplementedError()
        [func.apply(items, *args, **kwargs) for func in self.functions]
        return items


class LootTablePool:
    @classmethod
    def from_data(cls, table, data: dict):
        obj = cls()
        obj.table = table
        if "conditions" in data:
            obj.conditions = [cond for cond in data["conditions"]]
        if "functions" in data:
            obj.functions = [func for func in data["functions"]]
        if "entries" in data:
            obj.entries = [LootTablePoolEntry.from_data(obj, d) for d in data["entries"]]
            obj.entry_weights = [entry.weight for entry in obj.entries]
        return obj

    def __init__(self):
        self.conditions = []
        self.functions = []
        self.roll_range = (0, 0)
        self.bonus_roll_range = (0, 0)
        self.entries = []
        self.entry_weights = []
        self.table = None

    def roll(self, *args, **kwargs):
        if not all([condition.check(self, *args, **kwargs) for condition in self.conditions]): return []
        items = []
        i = random.randint(*self.roll_range)
        # todo: add bonus rolls
        while i > 0:
            item = random.choices(self.entries, weights=self.entry_weights)[0].roll(*args, **kwargs)
            if item is not None:
                items.append(item)
                i -= 1
        [func.apply(items) for func in self.functions]
        return items


class LootTable:
    @classmethod
    def from_file(cls, file: str, name=None):
        if name is None:
            s = file.split("/")
            name = "{}:{}/{}".format(s[s.index("data")+1], s[s.index("data")+3],
                                     "/".join(s[s.index("data")+4:]).split(".")[0])
        cls.from_data(ResourceLocator.read(file, "json"), name)

    @classmethod
    def from_data(cls, data: dict, name: str):
        obj = cls(LootTableTypes[data["type"]])
        handler.loot_tables[name] = obj
        [obj.pools.append(LootTablePool.from_data(obj, d)) for d in data["pools"]]
        return obj

    def __init__(self, table_type=LootTableTypes.UNSET):
        self.table_type = table_type
        self.pools = []

    def roll(self, *args, **kwargs):
        data = []
        [data.extend(pool.roll(*args, **kwargs) for pool in self.pools)]
        return data

