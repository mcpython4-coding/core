import event.Registry
import globals as G
import random


class ILootTableCondition(event.Registry.IRegistryContent):
    TYPE = "minecraft:loot_table_condition"

    def __init__(self, data: dict):
        self.data = data

    def check(self, source, *args, **kwargs) -> bool:
        return False


loottableconditionregistry = event.Registry.Registry("loot_table_registry", ["minecraft:loot_table_condition"])


@G.registry
class Alternative(ILootTableCondition):
    NAME = "minecraft:alternative"

    def __init__(self, data):
        super().__init__(data)
        self.conditions = [G.loottablehandler.parse_condition(d) for d in data["terms"]]

    def check(self, source, *args, **kwargs) -> bool:
        return any([condition.check(source, *args, **kwargs) for condition in self.conditions])


@G.registry
class BlockStateProperty(ILootTableCondition):
    NAME = "minecraft:block_state_property"
    # todo: implement


@G.registry
class DamageSourceProperties(ILootTableCondition):
    NAME = "minecraft:damage_source_properties"
    # todo: implement


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
        self.term = G.loottablehandler.parse_condition(data["term"])

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
        return random.randint(1, round(1/self.data["chance"])) == 1


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

    def check(self, source, *args, **kwargs) -> bool: return True


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



