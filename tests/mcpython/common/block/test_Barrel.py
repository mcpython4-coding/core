from unittest import TestCase

from mcpython import shared
from pyglet.window import key, mouse


class FakeInventoryHandler:
    SHOWN = False

    @classmethod
    def add(cls, inventory):
        return

    @classmethod
    def show(cls, inventory):
        cls.SHOWN = True


class FakeCraftingHandler:
    def __call__(self, *args, **kwargs):
        pass


class FakeWorld:
    @classmethod
    def get_dimension_by_name(cls, name: str):
        return cls

    @classmethod
    def get_chunk_for_position(cls, position):
        return cls

    @classmethod
    def exposed_faces(cls, position):
        return {}

    @classmethod
    def mark_position_dirty(cls, position):
        pass

    @classmethod
    def get_active_dimension(cls):
        return cls


class TestBarrel(TestCase):
    def test_module_import(self):
        shared.crafting_handler = FakeCraftingHandler()

        import mcpython.common.block.Barrel

        self.assertEqual(mcpython.common.block.Barrel.Barrel.NAME, "minecraft:barrel")

    def test_on_block_added(self):
        shared.crafting_handler = FakeCraftingHandler()
        shared.world = FakeWorld

        import mcpython.common.block.Barrel

        shared.inventory_handler = FakeInventoryHandler

        instance = mcpython.common.block.Barrel.Barrel()
        instance.position = 0, 0, 0
        instance.set_to = 0, -1, 0

        instance.on_block_added()

        self.assertEqual(instance.facing, "down")

        instance.set_to = 0, 0, 1

        instance.on_block_added()

        self.assertEqual(instance.facing, "south")

        shared.world = None

    def test_on_player_interaction(self):
        shared.crafting_handler = FakeCraftingHandler()

        import mcpython.common.block.Barrel

        shared.inventory_handler = FakeInventoryHandler
        FakeInventoryHandler.SHOWN = False

        instance = mcpython.common.block.Barrel.Barrel()

        instance.on_player_interaction(None, mouse.RIGHT, 0, None)

        self.assertTrue(FakeInventoryHandler.SHOWN)

        FakeInventoryHandler.SHOWN = False

        instance.on_player_interaction(None, mouse.RIGHT, key.MOD_SHIFT, None)

        self.assertFalse(FakeInventoryHandler.SHOWN)

    def test_model_state_serialization(self):
        shared.crafting_handler = FakeCraftingHandler()

        import mcpython.common.block.Barrel

        shared.inventory_handler = FakeInventoryHandler

        instance = mcpython.common.block.Barrel.Barrel()
        state = instance.get_model_state()
        instance.set_model_state({"facing": "north", "open": "true"})
        self.assertNotEqual(state, instance.get_model_state())
        instance.set_model_state(state)
        self.assertEqual(state, instance.get_model_state())
