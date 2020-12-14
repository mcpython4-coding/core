"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.event.Registry
import mcpython.common.entity.DamageSource
from mcpython import shared as G
import random


class ILootTableCondition(mcpython.common.event.Registry.IRegistryContent):
    TYPE = "minecraft:loot_table_condition"

    def __init__(self, data: dict):
        self.data = data

    def check(self, source, *args, **kwargs) -> bool:
        return False


loot_table_condition_registry = mcpython.common.event.Registry.Registry(
    "minecraft:loot_table_registry",
    ["minecraft:loot_table_condition"],
    "stage:loottables:conditions",
)


@G.registry
class Alternative(ILootTableCondition):
    NAME = "minecraft:alternative"

    def __init__(self, data):
        super().__init__(data)
        self.conditions = [
            G.loot_table_handler.parse_condition(d) for d in data["terms"]
        ]

    def check(self, source, *args, **kwargs) -> bool:
        return any(
            [condition.check(source, *args, **kwargs) for condition in self.conditions]
        )


@G.registry
class BlockStateProperty(ILootTableCondition):
    NAME = "minecraft:block_state_property"

    def __init__(self, data):
        super().__init__(data)
        self.name = data["block"]
        self.state = data["properties"] if "properties" in data else {}

    def check(self, source, *args, block=None, **kwargs) -> bool:
        if block is None:
            return False
        if block.NAME != self.name:
            return False
        if len(self.state) == 0:
            return True
        state = block.get_model_state()
        for key in self.state:
            if key not in state or state[key] != self.state[key]:
                return False
        return True


@G.registry
class DamageSourceProperties(ILootTableCondition):
    NAME = "minecraft:damage_source_properties"

    def __init__(self, data):
        super().__init__(data)
        self.source = mcpython.common.entity.DamageSource.DamageSource()
        if "bypasses_armor" in data:
            self.source.setAttribute("bypasses_armor", data["bypasses_armor"])
        if "bypasses_invulnerability" in data:
            self.source.setAttribute(
                "bypasses_invulnerability", data["bypasses_invulnerability"]
            )
        if "bypasses_magic" in data:
            self.source.setAttribute("bypasses_magic", data["bypasses_magic"])
        if "is_explosion" in data:
            self.source.setAttribute("is_explosion", data["is_explosion"])
        if "is_magic" in data:
            self.source.setAttribute("is_magic", data["is_magic"])
        if "is_projectile" in data:
            self.source.setAttribute("is_projectile", data["is_projectile"])
        if "is_lightning" in data:
            self.source.setAttribute("is_lightning", data["is_lightning"])

        # todo: add direct_entity & source_entity

    def check(self, source, *args, damage_source=None, **kwargs) -> bool:
        if damage_source is None:
            return False
        return self.source == damage_source


@G.registry
class EntityProperties(ILootTableCondition):
    NAME = "minecraft:entity_properties"
    # todo: implement


@G.registry
class EntityScores(ILootTableCondition):
    NAME = "minecraft:entity_scores"
    # todo: implement


@G.registry
class Inverted(ILootTableCondition):
    NAME = "minecraft:inverted"

    def __init__(self, data):
        super().__init__(data)
        self.term = G.loot_table_handler.parse_condition(data["term"])

    def check(self, source, *args, **kwargs) -> bool:
        return not self.term.check(source, *args, **kwargs)


@G.registry
class KilledByPlayer(ILootTableCondition):
    NAME = "minecraft:killed_by_player"
    # todo: implement


@G.registry
class LocationCheck(ILootTableCondition):
    NAME = "minecraft:location_check"
    # todo: implement


@G.registry
class MatchTool(ILootTableCondition):
    NAME = "minecraft:match_tool"
    # todo: implement


@G.registry
class RandomChance(ILootTableCondition):
    NAME = "minecraft:random_chance"

    def check(self, source, *args, **kwargs) -> bool:
        return random.randint(1, round(1 / self.data["chance"])) == 1


@G.registry
class RandomChanceWithLooting(RandomChance):
    NAME = "minecraft:random_chance_with_looting"
    # todo: implement looting


@G.registry
class Reference(ILootTableCondition):
    NAME = "minecraft:reference"
    # todo: implement


@G.registry
class SurvivesExplosion(ILootTableCondition):
    NAME = "minecraft:survives_explosion"
    # todo: implement

    def check(self, source, *args, **kwargs) -> bool:
        return True


@G.registry
class TableBonus(ILootTableCondition):
    NAME = "minecraft:table_bonus"
    # todo: implement


@G.registry
class TimeCheck(ILootTableCondition):
    NAME = "minecraft:time_check"
    # todo: implement


@G.registry
class ToolEnchantment(ILootTableCondition):
    NAME = "minecraft:tool_enchantment"
    # todo: implement


@G.registry
class WeatherCheck(ILootTableCondition):
    NAME = "minecraft:weather_check"
    # todo: implement
