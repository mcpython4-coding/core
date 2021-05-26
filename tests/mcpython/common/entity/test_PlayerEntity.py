from unittest import TestCase

from mcpython import shared

shared.IS_TEST_ENV = True


class FakeMod:
    class eventbus:
        @classmethod
        def subscribe(cls, *_, **__):
            pass


class FakeModloader:
    def __init__(self):
        self.finished = False

    def __call__(self, *args, **kwargs):
        return lambda func: None

    def __getitem__(self, item):
        return FakeMod


class TestPlayerEntity(TestCase):
    def test_module_import(self):
        import mcpython.common.entity.PlayerEntity

    def test_constructor(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")

        self.assertEqual(instance.name, "test_player")

    def test_set_gamemode(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")

        instance.set_gamemode(1)

        self.assertEqual(instance.gamemode, 1)

        instance.set_gamemode("survival")

        self.assertEqual(instance.gamemode, 0)

    def test_set_active_inventory_slot(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")

        instance.set_active_inventory_slot(3)
        self.assertEqual(instance.active_inventory_slot, 3)

        instance.set_active_inventory_slot(-1)
        self.assertEqual(instance.active_inventory_slot, 0)

        instance.set_active_inventory_slot(100)
        self.assertEqual(instance.active_inventory_slot, 8)

    def test_on_inventory_cleared(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")
        instance.xp = 0
        instance.xp_level = 0

        instance.on_inventory_cleared()

        self.assertEqual(instance.xp, 0)
        self.assertEqual(instance.xp_level, 0)
