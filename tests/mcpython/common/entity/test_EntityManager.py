import uuid
from unittest import TestCase

from mcpython import shared

shared.IS_TEST_ENV = True


class BaseTestEntity:
    def __init__(self, position=(0, 0, 0), child=None):
        self.uuid = uuid.uuid4()
        self.position = position
        self.parent = None
        self.child = child
        self.nbt_data = {"invulnerable": False}
        self.dimension = None
        self.entity_height = 1

    @classmethod
    def teleport(cls, position, force_chunk_save_update=False):
        pass

    @classmethod
    def tick(cls, dt: float):
        pass

    @classmethod
    def kill(cls, *_, **__):
        pass


class TestEntityManager(TestCase):
    def __init__(self, func=None):
        super().__init__(func)

        self.entity_manager_instance = None

    def ensure_setup(self):
        if self.entity_manager_instance is not None:
            return

        import mcpython.common.entity.EntityManager

        self.entity_manager_instance = (
            mcpython.common.entity.EntityManager.EntityManager()
        )

    def test_module_import(self):
        import mcpython.common.entity.EntityManager

    def test_add_entity_cls(self):
        self.ensure_setup()

        shared.IS_CLIENT = True

        successful_callback = False

        class TestEntity(BaseTestEntity):
            @classmethod
            def init_renderers(cls):
                nonlocal successful_callback
                successful_callback = True

        shared.IS_TEST_ENV = False

        self.entity_manager_instance.add_entity_cls(None, TestEntity)

        self.assertTrue(successful_callback)

        shared.IS_TEST_ENV = True

    def test_spawn_entity_from_class(self):
        self.ensure_setup()

        teleport_success = False

        class TestEntity(BaseTestEntity):
            @classmethod
            def teleport(cls, position, force_chunk_save_update=False):
                nonlocal teleport_success
                teleport_success = True

                self.assertEqual(position, (0, 0, 0))

        instance = TestEntity()

        self.entity_manager_instance.spawn_entity(instance, (0, 0, 0))

        self.assertTrue(teleport_success)
        self.assertIn(instance.uuid, self.entity_manager_instance.entity_map)
        self.assertEqual(
            self.entity_manager_instance.entity_map[instance.uuid], instance
        )

    def test_tick(self):
        self.ensure_setup()

        ticked = False

        class TestEntity(BaseTestEntity):
            @classmethod
            def tick(cls, dt: float):
                nonlocal ticked
                ticked = True

                self.assertEqual(dt, 0.05)

        instance = TestEntity()

        self.entity_manager_instance.spawn_entity(instance, (0, 0, 0))
        self.entity_manager_instance.tick(0.05)

        self.assertTrue(ticked)

    def test_tick_kill(self):
        self.ensure_setup()

        killed = False

        class TestEntity(BaseTestEntity):
            @classmethod
            def kill(cls):
                nonlocal killed
                killed = True

        instance = TestEntity(position=(0, -1001, 0))

        self.entity_manager_instance.spawn_entity(instance, (0, -1001, 0))
        self.entity_manager_instance.tick(0.05)

        self.assertTrue(killed)

    def test_tick_child_handling(self):
        """
        Checks if passenger handling works as it is expected
        Spawns to entities, links them and ticks the handler ones
        """
        self.ensure_setup()

        parent = BaseTestEntity()
        child = BaseTestEntity(position=(0, -20, 0))
        parent.child = child
        child.parent = parent

        self.entity_manager_instance.spawn_entity(parent, (0, 0, 0))
        self.entity_manager_instance.spawn_entity(child, (0, 0, 0))
        self.entity_manager_instance.tick(0.05)

        self.assertEqual(child.position, (0, 1, 0))

    def test_clear(self):
        self.ensure_setup()

        instance = BaseTestEntity()
        self.entity_manager_instance.spawn_entity(instance, (0, 0, 0))
        self.entity_manager_instance.clear()

        self.assertEqual(len(self.entity_manager_instance.entity_map), 0)
