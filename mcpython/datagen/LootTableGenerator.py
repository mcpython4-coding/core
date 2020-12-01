"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G, logger
import typing
import mcpython.datagen.Configuration


class ILootTableCondition:
    def serialize(self):
        raise NotImplementedError()


class ILootTableFunction:
    def serialize(self):
        raise NotImplementedError()


class ApplyBonus(ILootTableFunction):
    def __init__(self, enchantment: str, formula: str = "uniform_bonus_count", extra=None, probability=None,
                 bonus_multiplier=None, conditions=None):
        self.enchantment = enchantment
        self.formula = formula
        self.extra = extra
        self.probability = probability
        self.bonus_multiplier = bonus_multiplier
        self.conditions = conditions

    def serialize(self):
        d = {"function": "apply_bonus", "enchantment": self.enchantment, "formula": self.formula}
        if self.extra is not None or self.probability is not None or self.bonus_multiplier is not None:
            d["parameters"] = {}
            if self.extra is not None: d["parameters"]["extra"] = self.extra
            if self.probability is not None: d["parameters"]["probability"] = self.probability
            if self.bonus_multiplier is not None: d["parameters"]["bonusMultiplier"] = self.bonus_multiplier
        if self.conditions is not None:
            d["conditions"] = [condition.serialize() for condition in self.conditions]
        return d


class CopyName(ILootTableFunction):
    def serialize(self):
        return {"source": "block_entity", "function": "copy_name"}


class NBTCopyOperation:
    def __init__(self, nbt_source: str, nbt_target: str = None, op="merge"):
        self.nbt_source = nbt_source
        self.nbt_target = nbt_target if nbt_target is not None else nbt_source
        self.op = op

    def serialize(self):
        return {"source": self.nbt_source, "target": self.nbt_target, "op": self.op}


class CopyNBT(ILootTableFunction):
    def __init__(self, source: str, *operations: NBTCopyOperation):
        self.source = source
        self.operations = list(operations)

    def addOperation(self, operation: NBTCopyOperation):
        self.operations.append(operation)
        return self

    def serialize(self):
        return {"source": self.source, "ops": [operation.serialize() for operation in self.operations], "function": "copy_nbt"}


class CopyState(ILootTableFunction):
    def __init__(self, block: str, *properties: str):
        self.copy_properties = list(properties)
        self.block = block

    def addProperty(self, *properties: str):
        self.copy_properties.extend(properties)
        return self

    def serialize(self):
        return {"function": "copy_state", "block": self.block, "properties": self.copy_properties}


class EnchantRandomly(ILootTableFunction):
    def __init__(self, *enchantments: str):
        self.enchantments = list(enchantments)

    def addEnchantment(self, *enchanments: str):
        self.enchantments.extend(enchanments)
        return self

    def serialize(self):
        return {"function": "enchant_randomly", "enchantments": self.enchantments}


class ILootTableEntry:
    def __init__(self, weight=1, quality=1):
        self.weight = weight
        self.quality = quality
        self.conditions = []
        self.functions = []

    def addCondition(self, condition: ILootTableCondition):
        self.conditions.append(condition)
        return self

    def addFunction(self, function: ILootTableFunction):
        self.functions.append(function)
        return self

    def serialize(self) -> typing.Dict[str, typing.Any]:
        return {"conditions": [condition.serialize() for condition in self.conditions], "weight": self.weight,
                "functions": [function.serialize() for function in self.functions], "quality": self.quality}


class ItemLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1):
        super().__init__(weight, quality)
        self.item_name = None

    def setItemName(self, name: str):
        self.item_name = name
        return self

    def serialize(self):
        data = super().serialize()
        data["type"] = "item"
        data["name"] = self.item_name
        return self


class TagLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1, expand=False):
        super().__init__(weight, quality)
        self.tag_name = None
        self.expand = expand

    def setTagName(self, name: str):
        self.tag_name = name
        return self

    def serialize(self):
        data = super().serialize()
        data["type"] = "tag"
        data["name"] = self.tag_name
        data["expand"] = self.expand
        return self


class LootTableLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1):
        super().__init__(weight, quality)
        self.loot_table_name = None

    def setLootTable(self, name: str):
        self.loot_table_name = name
        return self

    def serialize(self):
        data = super().serialize()
        data["type"] = "loot_table"
        data["name"] = self.loot_table_name
        return self


class GroupLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1):
        super().__init__(weight, quality)
        self.children = []

    def addChild(self, child: ILootTableEntry):
        self.children.append(child)
        return self

    def serialize(self):
        data = super().serialize()
        data["type"] = "group"
        data["children"] = [child.serialize() for child in self.children]
        return self


class AlternativesLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1):
        super().__init__(weight, quality)
        self.children = []

    def addChild(self, child: ILootTableEntry):
        self.children.append(child)
        return self

    def serialize(self):
        data = super().serialize()
        data["type"] = "alternatives"
        data["children"] = [child.serialize() for child in self.children]
        return self


class SequenceLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1):
        super().__init__(weight, quality)
        self.children = []

    def addChild(self, child: ILootTableEntry):
        self.children.append(child)
        return self

    def serialize(self):
        data = super().serialize()
        data["type"] = "sequence"
        data["children"] = [child.serialize() for child in self.children]
        return self


class DynamicLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1):
        super().__init__(weight, quality)
        self.ref_name = None

    def setRefName(self, name: str):
        self.ref_name = name
        return self

    def serialize(self):
        data = super().serialize()
        data["type"] = "dynamic"
        data["name"] = self.ref_name
        return self


class LootTablePool:
    def __init__(self, rolls: typing.Union[int, typing.Tuple[int, int]] = 1, bonus_rolls: typing.Union[int, typing.Tuple[int, int]] = 1):
        self.rolls = rolls
        self.bonus_rolls = bonus_rolls
        self.conditions = []
        self.functions = []
        self.entries = []

    def addCondition(self, condition: ILootTableCondition):
        pass

    def addFunction(self, function: ILootTableFunction):
        pass

    def addEntry(self, entry: ILootTableEntry):
        pass

    def serialize(self):
        return {"entries": [entry.serialize() for entry in self.entries], "functions": [function.serialize() for function in self.functions],
                "conditions": [condition.serialize() for condition in self.conditions], "rolls": self.rolls, "bonus_rolls": self.bonus_rolls}


class LootTableGenerator(mcpython.datagen.Configuration.IDataGenerator):
    def __init__(self, config, name):
        super().__init__(config)
        self.name = name
        self.type = None
        self.pools = []

    def setType(self, t):
        self.type = t
        return self

    def addPool(self, pool: LootTablePool):
        self.pools.append(pool)
        return self

    def generate(self):
        data = {"pools": []}
        if self.type is not None: data["type"] = self.type
        for i, pool in enumerate(self.pools):
            try:
                data["pools"].append(pool.serialize())
            except:
                logger.println("during serializing {} (number {})".format(pool, i + 1))
                raise
        self.config.write_json(data, "data", "loot_tables", self.name+".json")



