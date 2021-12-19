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


class TestEventBus(TestCase):
    def test_import(self):
        import mcpython.engine.event.EventBus

    def test_constructor(self):
        import mcpython.engine.event.EventBus
        from mcpython import shared

        shared.NEXT_EVENT_BUS_ID = 10

        instance = mcpython.engine.event.EventBus.EventBus()
        self.assertEqual(instance.id, 10, "id read from shared")
        self.assertEqual(shared.NEXT_EVENT_BUS_ID, 11, "id increment on shared")

    def test_subscribe(self):
        from mcpython.engine.event.EventBus import EventBus

        def test():
            pass

        bus = EventBus()

        self.assertEqual(len(bus.event_subscriptions), 0)

        bus.subscribe("test_event", test)

        self.assertIn("test_event", bus.event_subscriptions)

        self.assertTrue(any(test in e for e in bus.event_subscriptions["test_event"]))

    def test_unsubscribe(self):
        from mcpython.engine.event.EventBus import EventBus

        def test():
            pass

        bus = EventBus()

        self.assertRaises(ValueError, lambda: bus.unsubscribe("test_event", test))

        bus.subscribe("test_event", test)
        bus.unsubscribe("test_event", test)

        self.assertRaises(ValueError, lambda: bus.unsubscribe("test_event", test))

    def test_call(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test():
            nonlocal state
            state = True

        bus = EventBus()
        bus.subscribe("test_event", test)
        bus.call("test_event")

        self.assertTrue(state)

    async def test_call_async(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test():
            nonlocal state
            state = True

        bus = EventBus()
        bus.subscribe("test_event", test)
        await bus.call_async("test_event")

        self.assertTrue(state)

    def test_call_args(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test(flag):
            nonlocal state
            state = flag

        bus = EventBus()
        bus.subscribe("test_event", test)
        bus.call("test_event", True)

        self.assertTrue(state)

    async def test_call_args_async(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test(flag):
            nonlocal state
            state = flag

        bus = EventBus()
        bus.subscribe("test_event", test)
        await bus.call_async("test_event", True)

        self.assertTrue(state)

    def test_call_with_subscriber_args(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test(flag):
            nonlocal state
            state = flag

        bus = EventBus()
        bus.subscribe("test_event", test, True)
        bus.call("test_event")

        self.assertTrue(state)

    async def test_call_with_subscriber_args_async(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test(flag):
            nonlocal state
            state = flag

        bus = EventBus()
        bus.subscribe("test_event", test, True)
        await bus.call_async("test_event")

        self.assertTrue(state)

    def test_call_with_args_and_subscriber_args(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test(flag1, flag2):
            nonlocal state
            state = flag1 and flag2

        bus = EventBus()
        bus.subscribe("test_event", test, True)
        bus.call("test_event", True)

        self.assertTrue(state)

    async def test_call_with_args_and_subscriber_args_async(self):
        from mcpython.engine.event.EventBus import EventBus

        state = False

        def test(flag1, flag2):
            nonlocal state
            state = flag1 and flag2

        bus = EventBus()
        bus.subscribe("test_event", test, True)
        await bus.call_async("test_event", True)

        self.assertTrue(state)

    def test_call_cancelable(self):
        from mcpython.engine.event.EventBus import CancelAbleEvent, EventBus

        calls = 0

        def test(cancel: CancelAbleEvent):
            nonlocal calls
            calls += 1

            cancel.cancel()

        bus = EventBus()
        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)

        result = bus.call_cancelable("test_event")
        self.assertTrue(result.canceled)
        self.assertEqual(calls, 1)

    async def test_call_cancelable_async(self):
        from mcpython.engine.event.EventBus import CancelAbleEvent, EventBus

        calls = 0

        def test(cancel: CancelAbleEvent):
            nonlocal calls
            calls += 1

            cancel.cancel()

        bus = EventBus()
        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)

        result = await bus.call_cancelable_async("test_event")
        self.assertTrue(result.canceled)
        self.assertEqual(calls, 1)

    def test_call_as_stack(self):
        from mcpython.engine.event.EventBus import EventBus

        invoked = False

        def test():
            nonlocal invoked
            invoked = True

        bus = EventBus()

        bus.subscribe("test_event", test)
        bus.call_as_stack("test_event")

        self.assertTrue(invoked)
        self.assertRaises(ValueError, lambda: bus.unsubscribe("test_event", test))

    async def test_call_as_stack_async(self):
        from mcpython.engine.event.EventBus import EventBus

        invoked = False

        def test():
            nonlocal invoked
            invoked = True

        bus = EventBus()

        bus.subscribe("test_event", test)
        await bus.call_as_stack_async("test_event")

        self.assertTrue(invoked)
        self.assertRaises(ValueError, lambda: bus.unsubscribe("test_event", test))

    def test_call_as_stack_no_result(self):
        from mcpython.engine.event.EventBus import EventBus

        invoked = False

        def test():
            nonlocal invoked
            invoked = True

        bus = EventBus()

        bus.subscribe("test_event", test)
        bus.call_as_stack_no_result("test_event")

        self.assertTrue(invoked)
        self.assertRaises(ValueError, lambda: bus.unsubscribe("test_event", test))

    async def test_call_as_stack_no_result_async(self):
        from mcpython.engine.event.EventBus import EventBus

        invoked = False

        def test():
            nonlocal invoked
            invoked = True

        bus = EventBus()

        bus.subscribe("test_event", test)
        await bus.call_as_stack_no_result_async("test_event")

        self.assertTrue(invoked)
        self.assertRaises(ValueError, lambda: bus.unsubscribe("test_event", test))

    def test_call_as_stack_multi(self):
        from mcpython.engine.event.EventBus import EventBus

        invoke_times = 0

        def test():
            nonlocal invoke_times
            invoke_times += 1

        bus = EventBus()

        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)

        bus.call_as_stack("test_event")

        self.assertEqual(invoke_times, 1)

    async def test_call_as_stack_multi_async(self):
        from mcpython.engine.event.EventBus import EventBus

        invoke_times = 0

        def test():
            nonlocal invoke_times
            invoke_times += 1

        bus = EventBus()

        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)

        await bus.call_as_stack_async("test_event")

        self.assertEqual(invoke_times, 1)

    def test_call_as_stack_multi_2(self):
        from mcpython.engine.event.EventBus import EventBus

        invoke_times = 0

        def test():
            nonlocal invoke_times
            invoke_times += 1

        bus = EventBus()

        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)

        bus.call_as_stack("test_event", amount=2)

        self.assertEqual(invoke_times, 2)

    async def test_call_as_stack_multi_2_async(self):
        from mcpython.engine.event.EventBus import EventBus

        invoke_times = 0

        def test():
            nonlocal invoke_times
            invoke_times += 1

        bus = EventBus()

        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)
        bus.subscribe("test_event", test)

        await bus.call_as_stack_async("test_event", amount=2)

        self.assertEqual(invoke_times, 2)

    def test_reset_event_stack(self):
        from mcpython.engine.event.EventBus import EventBus

        def test():
            pass

        bus = EventBus()

        bus.subscribe("test_event", test)
        bus.call_as_stack("test_event")
        bus.reset_event_stack("test_event")
        bus.unsubscribe("test_event", test)

    async def test_reset_event_stack_when_async(self):
        from mcpython.engine.event.EventBus import EventBus

        def test():
            pass

        bus = EventBus()

        bus.subscribe("test_event", test)
        await bus.call_as_stack_async("test_event")
        bus.reset_event_stack("test_event")
        bus.unsubscribe("test_event", test)
