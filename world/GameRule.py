import event.Registry
import globals as G


class GameRuleDataType:
    @classmethod
    def is_valid_value(cls, data: str): raise NotImplementedError()

    def copy(self): raise NotImplementedError()


class GameRuleTypeBoolean(GameRuleDataType):
    @classmethod
    def is_valid_value(cls, data: str):
        data = data.lower()
        return data in ("true", "false", "1", "0")

    def __init__(self, data: str):
        data = data.lower()
        self.status = data in ("true", "1")

    def copy(self): return GameRuleTypeBoolean(str(self.status))


class GameRuleTypeInt(GameRuleDataType):
    @classmethod
    def is_valid_value(cls, data: str):
        try:
            int(data)
            return True
        except:
            return False

    def __init__(self, data: str):
        self.status = int(data)

    def copy(self): return GameRuleTypeInt(str(self.status))


class GameRule(event.Registry.IRegistryContent):
    TYPE = "minecraft:game_rule"
    VALUE_TYPE = GameRuleDataType
    DEFAULT_VALUE = None

    def __init__(self, world):
        self.status = self.DEFAULT_VALUE
        self.world = world

    def set_status(self, value: str):
        self.status = self.VALUE_TYPE(value)


gamerule_registry = event.Registry.Registry("gamerule", ["minecraft:game_rule"])


@G.registry
class GameRuleDoImmediateRespawn(GameRule):
    NAME = "doImmediateRespawn"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("true")  # todo: change to false when correct DeathScreen is implemented


@G.registry
class GameRuleDoTileDrops(GameRule):
    NAME = "doTileDrops"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("true")


@G.registry
class GameRuleFallDamage(GameRule):
    NAME = "fallDamage"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("true")


@G.registry
class GameRuleKeepInventory(GameRule):
    NAME = "keepInventory"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("false")


@G.registry
class GameRuleNaturalRegeneration(GameRule):  # todo: implement
    NAME = "naturalRegeneration"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("true")


@G.registry
class GameRuleRandomTickSpeed(GameRule):
    NAME = "randomTickSpeed"
    VALUE_TYPE = GameRuleTypeInt
    DEFAULT_VALUE = GameRuleTypeInt("3")


@G.registry
class GameRuleShowCoordinates(GameRule):
    NAME = "showCoordinates"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("true")


@G.registry
class GameRuleShowDeathMessages(GameRule):
    NAME = "showDeathMessages"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("true")


@G.registry
class GameRuleSpawnRadius(GameRule):  # todo: implement
    NAME = "spawnRadius"
    VALUE_TYPE = GameRuleTypeInt
    DEFAULT_VALUE = GameRuleTypeInt("10")


@G.registry
class GameRuleSpectatorsGenerateChunks(GameRule):  # todo: implement
    NAME = "spectatorsGenerateChunks"
    VALUE_TYPE = GameRuleTypeBoolean
    DEFAULT_VALUE = GameRuleTypeBoolean("true")


class GameRuleHandler:
    def __init__(self, world):
        self.table = {}
        for gamerule in gamerule_registry.registered_object_map.keys():
            self.table[gamerule] = gamerule_registry.registered_object_map[gamerule](world)

