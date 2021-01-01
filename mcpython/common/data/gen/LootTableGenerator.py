"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from abc import ABC

from mcpython import shared, logger
import typing
from mcpython.common.data.gen.DataGeneratorManager import (
    IDataGenerator,
    DataGeneratorInstance,
)


class ILootTableCondition(IDataGenerator, ABC):
    pass


class ILootTableFunction(IDataGenerator, ABC):
    pass


class ApplyBonus(ILootTableFunction):
    def __init__(
        self,
        enchantment: str,
        formula: str = "uniform_bonus_count",
        extra=None,
        probability=None,
        bonus_multiplier=None,
        conditions=None,
    ):
        self.enchantment = enchantment
        self.formula = formula
        self.extra = extra
        self.probability = probability
        self.bonus_multiplier = bonus_multiplier
        self.conditions = conditions

    def dump(self, generator: DataGeneratorInstance):
        d = {
            "function": "apply_bonus",
            "enchantment": self.enchantment,
            "formula": self.formula,
        }
        if (
            self.extra is not None
            or self.probability is not None
            or self.bonus_multiplier is not None
        ):
            d["parameters"] = {}
            if self.extra is not None:
                d["parameters"]["extra"] = self.extra
            if self.probability is not None:
                d["parameters"]["probability"] = self.probability
            if self.bonus_multiplier is not None:
                d["parameters"]["bonusMultiplier"] = self.bonus_multiplier
        if self.conditions is not None:
            d["conditions"] = [condition.serialize() for condition in self.conditions]
        return d


class CopyName(ILootTableFunction):
    def dump(self, generator: DataGeneratorInstance):
        return {"source": "block_entity", "function": "copy_name"}


class NBTCopyOperation:
    def __init__(self, nbt_source: str, nbt_target: str = None, op="merge"):
        self.nbt_source = nbt_source
        self.nbt_target = nbt_target if nbt_target is not None else nbt_source
        self.op = op

    def dump(self, generator: DataGeneratorInstance):
        return {"source": self.nbt_source, "target": self.nbt_target, "op": self.op}


class CopyNBT(ILootTableFunction):
    def __init__(self, source: str, *operations: NBTCopyOperation):
        self.source = source
        self.operations = list(operations)

    def addOperation(self, operation: NBTCopyOperation):
        self.operations.append(operation)
        return self

    def dump(self, generator: DataGeneratorInstance):
        return {
            "source": self.source,
            "ops": [operation.dump(generator) for operation in self.operations],
            "function": "copy_nbt",
        }


class CopyState(ILootTableFunction):
    def __init__(self, block: str, *properties: str):
        self.copy_properties = list(properties)
        self.block = block

    def addProperty(self, *properties: str):
        self.copy_properties.extend(properties)
        return self

    def dump(self, generator: DataGeneratorInstance):
        return {
            "function": "copy_state",
            "block": self.block,
            "properties": self.copy_properties,
        }


class EnchantRandomly(ILootTableFunction):
    def __init__(self, *enchantments: str):
        self.enchantments = list(enchantments)

    def addEnchantment(self, *enchanments: str):
        self.enchantments.extend(enchanments)
        return self

    def dump(self, generator: DataGeneratorInstance):
        return {"function": "enchant_randomly", "enchantments": self.enchantments}


class ILootTableEntry(IDataGenerator):
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

    def dump(self, generator: DataGeneratorInstance):
        return {
            "conditions": [condition.dump(generator) for condition in self.conditions],
            "weight": self.weight,
            "functions": [function.dump(generator) for function in self.functions],
            "quality": self.quality,
        }


class ItemLootTableEntry(ILootTableEntry):
    def __init__(self, weight=1, quality=1):
        super().__init__(weight, quality)
        self.item_name = None

    def setItemName(self, name: str):
        self.item_name = name
        return self

    def dump(self, generator: DataGeneratorInstance):
        data = super().dump(generator)
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

    def dump(self, generator: DataGeneratorInstance):
        data = super().dump(generator)
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

    def dump(self, generator: DataGeneratorInstance):
        data = super().dump(generator)
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

    def dump(self, generator: DataGeneratorInstance):
        data = super().dump(generator)
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

    def dump(self, generator: DataGeneratorInstance):
        data = super().dump(generator)
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

    def dump(self, generator: DataGeneratorInstance):
        data = super().dump(generator)
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

    def dump(self, generator: DataGeneratorInstance):
        data = super().dump(generator)
        data["type"] = "dynamic"
        data["name"] = self.ref_name
        return self


class LootTablePool(IDataGenerator):
    def __init__(
        self,
        rolls: typing.Union[int, typing.Tuple[int, int]] = 1,
        bonus_rolls: typing.Union[int, typing.Tuple[int, int]] = 1,
    ):
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

    def dump(self, generator: DataGeneratorInstance):
        return {
            "entries": [entry.dump(generator) for entry in self.entries],
            "functions": [function.dump(generator) for function in self.functions],
            "conditions": [condition.dump(generator) for condition in self.conditions],
            "rolls": self.rolls,
            "bonus_rolls": self.bonus_rolls,
        }


class LootTableGenerator(IDataGenerator):
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

    def dump(self, generator: DataGeneratorInstance):
        data = {"pools": []}
        if self.type is not None:
            data["type"] = self.type
        for i, pool in enumerate(self.pools):
            try:
                data["pools"].append(pool.serialize())
            except:
                logger.println("during serializing {} (number {})".format(pool, i + 1))
                raise
        return data

    def get_default_location(self, generator: "DataGeneratorInstance", name: str):
        return (
            "data/{}/loot_tables/{}.json".format(*name.split(":"))
            if name.count(":") == 1
            else "data/{}/loot_tables/{}.json".format(generator.default_namespace, name)
        )
