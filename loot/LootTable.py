import ResourceLocator
import enum
import random
import gui.ItemStack
import globals as G
import mod.ModMcpython
import loot.LootTableCondition
import loot.LootTableFunction
import logger


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
        if name not in self.loot_tables:
            logger.println("loot table not found: '{}'".format(name))
            return []
        return self[name].roll(*args, **kwargs)

    def for_mod_name(self, modname, directoryname=None):
        if directoryname is None: directoryname = modname
        modinstance = G.modloader.mods[modname] if modname in G.modloader.mods else G.modloader.mods["minecraft"]
        for path in ResourceLocator.get_all_entries("data/{}/loot_tables".format(directoryname)):
            if path.endswith("/"): continue
            self._add_load(modinstance, path)

    def _add_load(self, modinstance, path):
        modinstance.eventbus.subscribe("stage:loottables:load", lambda: self.from_file(path),
                                       info="loading loot table '{}'".format(path))

    def from_file(self, file: str):
        LootTable.from_file(file)

    def parse_function(self, data: dict) -> loot.LootTableFunction.ILootTableFunction:
        name = data["function"]
        if name in loot.LootTableFunction.loottablefunctionregistry.registered_object_map:
            return loot.LootTableFunction.loottablefunctionregistry.registered_object_map[name](data)
        raise ValueError("unable to decode loot table function '{}'".format(name))

    def parse_condition(self, data: dict) -> loot.LootTableCondition.ILootTableCondition:
        name = data["condition"]
        if name in loot.LootTableCondition.loottableconditionregistry.registered_object_map:
            return loot.LootTableCondition.loottableconditionregistry.registered_object_map[name](data)
        raise ValueError("unable to decode loot table condition '{}'".format(name))

    def get_drop_for_block(self, block, player=None):
        table_name = "{}:blocks/{}".format(*block.NAME.split(":"))
        if table_name in self.loot_tables:
            return self.loot_tables[table_name].roll(block=block, player=player)
        return [gui.ItemStack.ItemStack(block.NAME)]


handler = G.loottablehandler = LootTableHandler()


class LootTablePoolEntry:
    @classmethod
    def from_data(cls, pool, data: dict):
        obj = cls(entry_type=LootTablePoolEntryType[data["type"].split(":")[-1].upper()])
        obj.pool = pool
        if "conditions" in data:
            obj.conditions = [handler.parse_condition(cond) for cond in data["conditions"]]
        if "functions" in data:
            obj.functions = [handler.parse_function(func) for func in data["functions"]]
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
            obj.conditions = [handler.parse_condition(cond) for cond in data["conditions"]]
        if "functions" in data:
            obj.functions = [handler.parse_function(func) for func in data["functions"]]
        if "entries" in data:
            obj.entries = [LootTablePoolEntry.from_data(obj, d) for d in data["entries"]]
            obj.entry_weights = [entry.weight for entry in obj.entries]
        if "rolls" in data:
            if type(data["rolls"]) in (int, float):
                obj.roll_range = (data["rolls"], data["rolls"])
            else:
                obj.roll_range = (data["rolls"]["min"], data["rolls"]["max"])
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
        done = []
        # todo: add bonus rolls
        while i > 0:
            entry = random.choices(self.entries, weights=self.entry_weights)[0]
            item = entry.roll(*args, **kwargs)
            if item is not None:
                items += item
                i -= 1
            else:
                if entry not in done: done.append(entry)
                elif len(done) == len(self.entries): break
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
        obj = cls(LootTableTypes[data["type"].split(":")[-1].upper()])
        handler.loot_tables[name] = obj
        if "pools" in data:
            [obj.pools.append(LootTablePool.from_data(obj, d)) for d in data["pools"]]
        return obj

    def __init__(self, table_type=LootTableTypes.UNSET):
        self.table_type = table_type
        self.pools = []

    def roll(self, *args, **kwargs):
        data = []
        for pool in self.pools:
            data += pool.roll(*args, **kwargs)
        return data


def init():
    handler.for_mod_name("minecraft")


mod.ModMcpython.mcpython.eventbus.subscribe("stage:loottables:locate", init)

