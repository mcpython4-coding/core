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
from unittest import TestCase


class TestEventHandler(TestCase):
    def test_import(self):
        import mcpython.engine.event.EventHandler

    def test_create_bus(self):
        from mcpython import shared
        from mcpython.engine.event.EventBus import EventBus
        from mcpython.engine.event.EventHandler import EventHandler

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus()

        self.assertIsInstance(bus, EventBus)
        self.assertIn(bus, shared.event_handler.buses)
        self.assertIn(bus, shared.event_handler.active_buses)

    def test_create_bus_not_active(self):
        from mcpython import shared
        from mcpython.engine.event.EventBus import EventBus
        from mcpython.engine.event.EventHandler import EventHandler

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus(active=False)
        self.assertIsInstance(bus, EventBus)
        self.assertIn(bus, shared.event_handler.buses)
        self.assertNotIn(bus, shared.event_handler.active_buses)

    def test_activate_bus(self):
        from mcpython import shared
        from mcpython.engine.event.EventHandler import EventHandler

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus(active=False)
        shared.event_handler.activate_bus(bus)
        self.assertIn(bus, shared.event_handler.active_buses)

    def test_deactivate_bus(self):
        from mcpython import shared
        from mcpython.engine.event.EventHandler import EventHandler

        shared.event_handler: EventHandler

        bus = shared.event_handler.create_bus()
        shared.event_handler.deactivate_bus(bus)

        self.assertNotIn(bus, shared.event_handler.active_buses)

    def test_call(self):
        from mcpython import shared
        from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS

        state = False

        def test():
            nonlocal state
            state = True

        PUBLIC_EVENT_BUS.subscribe("test_event", test)
        shared.event_handler.call("test_event")

        self.assertTrue(state)

    async def test_call_async(self):
        from mcpython import shared
        from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS

        state = False

        async def test():
            nonlocal state
            state = True

        PUBLIC_EVENT_BUS.subscribe("test_event", test())
        await shared.event_handler.call_async("test_event")

        self.assertTrue(state)
