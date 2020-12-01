"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.ResourceLocator
import enum
import mcpython.client.gui.ItemStack
from mcpython import shared as G, logger
import mcpython.common.mod.ModMcpython
import mcpython.common.data.loot.LootTableCondition
import mcpython.common.data.loot.LootTableFunction
import mcpython.common.event.EventHandler
import random


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
    BARTER = 9


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

        self.relink_table = {}
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "data:shuffle:all", self.shuffle_data
        )

        self.mod_names_to_load = set()

    def reload(self):
        self.loot_tables.clear()
        for modname in self.mod_names_to_load:
            self.for_mod_name(modname)
        G.eventhandler.call("data:loot_tables:custom_inject", self)

    def shuffle_data(self):
        ccopy = list(self.loot_tables.keys())
        for key in self.loot_tables:
            relinked = random.choice(ccopy)
            self.relink_table[key] = relinked
            ccopy.remove(relinked)

    def __getitem__(self, item):
        if item in self.relink_table:
            item = self.relink_table[item]
        return self.loot_tables[item]

    def roll(self, name: str, *args, relink=True, **kwargs) -> list:
        """
        will roll the loot table
        :param name: the name of the loot table
        :param args: args send to every part
        :param relink: if relinks should be followed or not
        :param kwargs: kwargs send to every part
        :return: an list of item stacks
        kwarg-options:
            - block=<Block instance>: an block parsed on
            - damage_source=<DamageSource instance>: an damage source
            - this_entity=<Entity instance>: an entity generated for
            - killer_entity=<Entity instance>:  the entity killed the this_entity
            - position=<tuple of lenght 3>: the position executed at
        """
        if name.count(":") == 0:
            name = "minecraft:" + name
        if relink and name in self.relink_table:
            name = self.relink_table[name]
        if name not in self.loot_tables:
            logger.println("loot table not found: '{}'".format(name))
            return []
        return self[name].roll(*args, **kwargs)

    def get_drop_for_block(self, block, player=None, relink=True):
        table_name = "{}:blocks/{}".format(*block.NAME.split(":"))
        if relink and table_name in self.relink_table:
            table_name = self.relink_table[table_name]
        if table_name in self.loot_tables:
            return self.loot_tables[table_name].roll(block=block, player=player)
        # todo: add option to print an warning here
        return [mcpython.client.gui.ItemStack.ItemStack(block.NAME)]

    def for_mod_name(self, modname, directoryname=None):
        if directoryname is None:
            directoryname = modname
        modinstance = (
            G.modloader.mods[modname]
            if modname in G.modloader.mods
            else G.modloader.mods["minecraft"]
        )
        for path in mcpython.ResourceLocator.get_all_entries(
            "data/{}/loot_tables".format(directoryname)
        ):
            if path.endswith("/"):
                continue
            self._add_load(modinstance, path)
        self.mod_names_to_load.add(modname)

    def _add_load(self, modinstance, path):
        modinstance.eventbus.subscribe(
            "stage:loottables:load",
            lambda: self.from_file(path),
            info="loading loot table '{}'".format(path),
        )

    def from_file(self, file: str):
        LootTable.from_file(file)

    def parse_function(
        self, data: dict
    ) -> mcpython.common.data.loot.LootTableFunction.ILootTableFunction:
        name = data["function"]
        if (
            name
            in mcpython.common.data.loot.LootTableFunction.loottablefunctionregistry.registered_object_map
        ):
            return mcpython.common.data.loot.LootTableFunction.loottablefunctionregistry.registered_object_map[
                name
            ](
                data
            )
        logger.println("unable to decode loot table function '{}'".format(name))

    def parse_condition(
        self, data: dict
    ) -> mcpython.common.data.loot.LootTableCondition.ILootTableCondition:
        name = data["condition"]
        if (
            name
            in mcpython.common.data.loot.LootTableCondition.loottableconditionregistry.registered_object_map
        ):
            return mcpython.common.data.loot.LootTableCondition.loottableconditionregistry.registered_object_map[
                name
            ](
                data
            )
        logger.println("unable to decode loot table condition '{}'".format(name))


handler = G.loottablehandler = LootTableHandler()


class LootTablePoolEntry:
    @classmethod
    def from_data(cls, pool, data: dict):
        obj = cls(
            entry_type=LootTablePoolEntryType[data["type"].split(":")[-1].upper()]
        )
        obj.pool = pool
        if "conditions" in data:
            obj.conditions = [
                handler.parse_condition(cond) for cond in data["conditions"]
            ]
        if "functions" in data:
            obj.functions = [handler.parse_function(func) for func in data["functions"]]
            while None in obj.functions:
                obj.functions.remove(None)
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
        if self.entry_type == LootTablePoolEntryType.UNSET:
            raise ValueError("type not set")
        if not all([cond.check(self, *args, **kwargs) for cond in self.conditions]):
            return None
        items = []
        if self.entry_type == LootTablePoolEntryType.ITEM:
            items.append(mcpython.client.gui.ItemStack.ItemStack(self.name))
        elif self.entry_type == LootTablePoolEntryType.TAG:
            if self.expand:
                items.append(
                    mcpython.client.gui.ItemStack.ItemStack(
                        random.choice(G.taghandler.get_tag_for(self.name, "items"))
                    )
                )
            else:
                items += [
                    mcpython.client.gui.ItemStack.ItemStack(name)
                    for name in G.taghandler.get_tag_for(self.name, "items")
                ]
        elif self.entry_type == LootTablePoolEntryType.LOOT_TABLE:
            items += handler.roll(self.name, *args, **kwargs)
        elif self.entry_type == LootTablePoolEntryType.GROUP:
            [items.extend(e.roll(*args, **kwargs)) for e in self.children]
        elif self.entry_type == LootTablePoolEntryType.ALTERNATIVES:
            for entry in self.children:
                item = entry.roll(*args, **kwargs)
                if item is None:
                    continue
                items += item
                break
        elif self.entry_type == LootTablePoolEntryType.SEQUENCE:
            for entry in self.children:
                item = entry.roll(*args, **kwargs)
                if item is None:
                    break
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
            obj.conditions = [
                handler.parse_condition(cond) for cond in data["conditions"]
            ]
        if "functions" in data:
            obj.functions = [handler.parse_function(func) for func in data["functions"]]
        if "entries" in data:
            obj.entries = [
                LootTablePoolEntry.from_data(obj, d) for d in data["entries"]
            ]
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
        if not all(
            [condition.check(self, *args, **kwargs) for condition in self.conditions]
        ):
            return []
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
                if entry not in done:
                    done.append(entry)
                elif len(done) == len(self.entries):
                    break
        [func.apply(items) for func in self.functions]
        return items


class LootTable:
    @classmethod
    def from_file(cls, file: str, name=None):
        if name is None:
            s = file.split("/")
            name = "{}:{}/{}".format(
                s[s.index("data") + 1],
                s[s.index("data") + 3],
                "/".join(s[s.index("data") + 4 :]).split(".")[0],
            )
        cls.from_data(mcpython.ResourceLocator.read(file, "json"), name)

    @classmethod
    def from_data(cls, data: dict, name: str):
        try:
            obj = cls(
                LootTableTypes[data["type"].split(":")[-1].upper()]
                if "type" in data
                else LootTableTypes.UNSET
            )
        except KeyError:
            if "type" in data:
                logger.println(
                    "[WARN] type '{}' not found for loot table '{}'!".format(
                        data["type"], name
                    )
                )
            else:
                logger.print_exception(
                    "[ERROR] fatal during loading loot table '{}'".format(name)
                )
            return
        except:
            logger.print_exception(
                "[ERROR] fatal during loading loot table '{}'".format(name)
            )
            return
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


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:loottables:locate", init
)
