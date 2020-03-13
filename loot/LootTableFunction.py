import event.Registry
import globals as G
import gui.ItemStack
import random


class ILootTableFunction(event.Registry.IRegistryContent):
    TYPE = "minecraft:loot_table_function"

    def __init__(self, data: dict):
        self.data = data

    def apply(self, items: list, *args, **kwargs):
        pass


loottablefunctionregistry = event.Registry.Registry("loottablefunctionregistry",
                                                    registry_type_names=["minecraft:loot_table_function"])


@G.registry
class ApplyBonus(ILootTableFunction):
    NAME = "minecraft:apply_bonus"

    def __init__(self, data: dict):
        super().__init__(data)
        self.enchantment = data["enchantment"]
        self.formula = data["formula"]
        self.parameters = data["parameters"] if "parameters" in data else {}

    def apply(self, items: list, *args, **kwargs):
        pass


@G.registry
class CopyName(ILootTableFunction):
    NAME = "minecraft:copy_name"

    def __init__(self, data: dict):
        super().__init__(data)
        self.source = data["source"]

    def apply(self, items: list, *args, **kwargs):
        if self.source == "block_entity":
            if "block" in kwargs:
                block = kwargs["block"]
                for item in items:
                    item.display_name = block.get_inventories()[0].custom_name


@G.registry
class CopyNBT(ILootTableFunction):
    NAME = "minecraft:copy_nbt"
    # todo: implement


@G.registry
class CopyState(ILootTableFunction):
    NAME = "minecraft:copy_state"
    # todo: implement


@G.registry
class EnchantRandomly(ILootTableFunction):
    NAME = "minecraft:enchant_randomly"
    # todo: implement


@G.registry
class EnchantWithLevels(ILootTableFunction):
    NAME = "minecraft:enchant_with_levels"
    # todo: implement


@G.registry
class ExplorationMap(ILootTableFunction):
    NAME = "minecraft:exploration_map"
    # todo: implement


@G.registry
class ExplosionDecay(ILootTableFunction):
    NAME = "minecraft:explosion_decay"
    # todo: implement


@G.registry
class FurnaceSmelt(ILootTableFunction):
    NAME = "minecraft:furnace_smelt"

    def apply(self, items: list, *args, **kwargs):
        for i, itemstack in enumerate(items.copy()):
            itemname = itemstack.get_item_name()
            if itemname is None: continue
            if itemname in G.craftinghandler.furnace_recipes["minecraft:smelting"]:
                result = G.craftinghandler.furnace_recipes["minecraft:smelting"][itemname]
                items[i] = gui.ItemStack.ItemStack(result.output, itemstack.amount)


@G.registry
class FillPlayerHead(ILootTableFunction):
    NAME = "minecraft:fill_player_head"
    # todo: implement


@G.registry
class LimitCount(ILootTableFunction):
    NAME = "minecraft:limit_count"
    # todo: implement


@G.registry
class LootingEnchant(ILootTableFunction):
    NAME = "minecraft:looting_enchant"
    # todo: implement


@G.registry
class SetAttributes(ILootTableFunction):
    NAME = "minecraft:set_attributes"
    # todo: implement


@G.registry
class SetContents(ILootTableFunction):
    NAME = "minecraft:set_contents"
    # todo: implement


@G.registry
class SetCount(ILootTableFunction):
    NAME = "minecraft:set_count"

    def apply(self, items: list, *args, **kwargs):
        for itemstack in items:
            if "count" in self.data:
                if type(self.data["count"]) == int:
                    itemstack.set_amount(self.data["count"])
                else:
                    if self.data["count"]["type"] == "minecraft:uniform":
                        count = random.randint(self.data["count"]["min"], self.data["count"]["max"])
                    elif self.data["count"]["type"] == "minecraft:binomial":
                        count = 0
                        for _ in range(self.data["count"]["n"]):
                            if random.randint(1, round(1/self.data["count"]["p"])) == 1: count += 1
                    else:
                        raise ValueError("unknown set type: '{}'".format(self.data["count"]["type"]))
                    itemstack.set_amount(count)


@G.registry
class SetDamage(ILootTableFunction):
    NAME = "minecraft:set_damage"
    # todo: implement


@G.registry
class SetLore(ILootTableFunction):
    NAME = "minecraft:set_lore"
    # todo: implement


@G.registry
class SetName(ILootTableFunction):
    NAME = "minecraft:set_name"
    # todo: implement


@G.registry
class SetNBT(ILootTableFunction):
    NAME = "minecraft:set_nbt"
    # todo: implement


@G.registry
class SetStewEffect(ILootTableFunction):
    NAME = "minecraft:set_stew_effect"
    # todo: implement

