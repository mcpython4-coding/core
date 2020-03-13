import event.Registry


class ILootTableCondition(event.Registry.IRegistryContent):
    TYPE = "minecraft:loot_table_condition"

    @classmethod
    def check(cls, source, *args, **kwargs) -> bool:
        return False

