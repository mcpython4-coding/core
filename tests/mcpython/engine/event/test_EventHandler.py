from unittest import TestCase


class TestEventHandler(TestCase):
    def test_import(self):
        import mcpython.engine.event.EventHandler

    def test_create_bus(self):
        from mcpython.engine.event.EventHandler import EventHandler
        from mcpython import shared
        from mcpython.engine.event.EventBus import EventBus

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus()

        self.assertIsInstance(bus, EventBus)
        self.assertIn(bus, shared.event_handler.buses)
        self.assertIn(bus, shared.event_handler.active_buses)

    def test_create_bus_not_active(self):
        from mcpython.engine.event.EventHandler import EventHandler
        from mcpython import shared
        from mcpython.engine.event.EventBus import EventBus

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus(active=False)
        self.assertIsInstance(bus, EventBus)
        self.assertIn(bus, shared.event_handler.buses)
        self.assertNotIn(bus, shared.event_handler.active_buses)

    def test_activate_bus(self):
        from mcpython.engine.event.EventHandler import EventHandler
        from mcpython import shared

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus(active=False)
        shared.event_handler.activate_bus(bus)
        self.assertIn(bus, shared.event_handler.active_buses)

    def test_deactivate_bus(self):
        from mcpython.engine.event.EventHandler import EventHandler
        from mcpython import shared

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus()
        shared.event_handler.deactivate_bus(bus)

        self.assertNotIn(bus, shared.event_handler.active_buses)

    def test_call(self):
        from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS
        from mcpython import shared

        state = False

        def test():
            nonlocal state
            state = True

        PUBLIC_EVENT_BUS.subscribe("test_event", test)
        shared.event_handler.call("test_event")

        self.assertTrue(state)
