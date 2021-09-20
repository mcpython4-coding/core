"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import random

import mcpython.common.container.ResourceStack
import mcpython.common.event.api
import mcpython.common.event.Registry
from mcpython import shared


class ILootTableFunction(mcpython.common.event.api.IRegistryContent):
    TYPE = "minecraft:loot_table_function"

    def __init__(self, data: dict):
        self.data = data

    def apply(self, items: list, *args, **kwargs):
        pass


loot_table_function_registry = mcpython.common.event.Registry.Registry(
    "minecraft:loot_table_function_registry",
    ["minecraft:loot_table_function"],
    "stage:loottables:functions",
)


@shared.registry
class ApplyBonus(ILootTableFunction):
    NAME = "minecraft:apply_bonus"

    def __init__(self, data: dict):
        super().__init__(data)
        self.enchantment = data["enchantment"]
        self.formula = data["formula"]
        self.parameters = data["parameters"] if "parameters" in data else {}

    def apply(self, items: list, *args, **kwargs):
        pass


@shared.registry
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


@shared.registry
class CopyNBT(ILootTableFunction):
    NAME = "minecraft:copy_nbt"
    # todo: implement


@shared.registry
class CopyState(ILootTableFunction):
    NAME = "minecraft:copy_state"
    # todo: implement


@shared.registry
class EnchantRandomly(ILootTableFunction):
    NAME = "minecraft:enchant_randomly"
    # todo: implement


@shared.registry
class EnchantWithLevels(ILootTableFunction):
    NAME = "minecraft:enchant_with_levels"
    # todo: implement


@shared.registry
class ExplorationMap(ILootTableFunction):
    NAME = "minecraft:exploration_map"
    # todo: implement


@shared.registry
class ExplosionDecay(ILootTableFunction):
    NAME = "minecraft:explosion_decay"
    # todo: implement


@shared.registry
class FurnaceSmelt(ILootTableFunction):
    NAME = "minecraft:furnace_smelt"

    def apply(self, items: list, *args, **kwargs):
        for i, itemstack in enumerate(items.copy()):
            itemname = itemstack.get_item_name()
            if itemname is None:
                continue
            if (
                itemname
                in shared.crafting_handler.furnace_recipes["minecraft:smelting"]
            ):
                result = shared.crafting_handler.furnace_recipes["minecraft:smelting"][
                    itemname
                ]
                items[i] = mcpython.common.container.ResourceStack.ItemStack(
                    result.output, itemstack.amount
                )


@shared.registry
class FillPlayerHead(ILootTableFunction):
    NAME = "minecraft:fill_player_head"
    # todo: implement


@shared.registry
class LimitCount(ILootTableFunction):
    NAME = "minecraft:limit_count"
    # todo: implement


@shared.registry
class LootingEnchant(ILootTableFunction):
    NAME = "minecraft:looting_enchant"
    # todo: implement


@shared.registry
class SetAttributes(ILootTableFunction):
    NAME = "minecraft:set_attributes"
    # todo: implement


@shared.registry
class SetContents(ILootTableFunction):
    NAME = "minecraft:set_contents"
    # todo: implement


@shared.registry
class SetCount(ILootTableFunction):
    NAME = "minecraft:set_count"

    def apply(self, items: list, *args, **kwargs):
        for itemstack in items:
            # todo: parse data in advance
            if "count" in self.data:
                if type(self.data["count"]) in (int, float):
                    itemstack.set_amount(int(self.data["count"]))
                else:
                    if self.data["count"]["type"] == "minecraft:uniform":
                        count = random.randint(
                            self.data["count"]["min"], self.data["count"]["max"]
                        )
                    elif self.data["count"]["type"] == "minecraft:binomial":
                        count = 0
                        for _ in range(self.data["count"]["n"]):
                            if (
                                random.randint(1, round(1 / self.data["count"]["p"]))
                                == 1
                            ):
                                count += 1
                    else:
                        raise ValueError(
                            "unknown set type: '{}'".format(self.data["count"]["type"])
                        )
                    itemstack.set_amount(count)


@shared.registry
class SetDamage(ILootTableFunction):
    NAME = "minecraft:set_damage"
    # todo: implement


@shared.registry
class SetLore(ILootTableFunction):
    NAME = "minecraft:set_lore"
    # todo: implement


@shared.registry
class SetName(ILootTableFunction):
    NAME = "minecraft:set_name"
    # todo: implement


@shared.registry
class SetNBT(ILootTableFunction):
    NAME = "minecraft:set_nbt"
    # todo: implement


@shared.registry
class SetStewEffect(ILootTableFunction):
    NAME = "minecraft:set_stew_effect"
    # todo: implement
