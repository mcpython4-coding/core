import event.Registry


class ILootTableFunction(event.Registry.IRegistryContent):
    TYPE = "minecraft:loot_table_function"

    @classmethod
    def apply(cls, items: list, *args, **kwargs):
        pass

