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
import mcpython.common.event.TickHandler
from mcpython import shared
from tests.util import TestCase


class Tickable:
    async def tick(self, *_):
        pass


class FakeNetwork:
    async def fetch_as_server(self):
        pass

    async def fetch_as_client(self):
        pass


class FakeTagHandler:
    entries = []

    def get_tag_for(self, name: str, _):
        return self


class TestTickHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        shared.entity_manager = Tickable()
        shared.world = Tickable()
        shared.NETWORK_MANAGER = FakeNetwork()
        shared.tag_handler = FakeTagHandler()

    @classmethod
    def tearDownClass(cls):
        shared.entity_manager = None
        shared.world = None
        shared.NETWORK_MANAGER = None
        shared.tag_handler = None

    def setUp(self):
        shared.tick_handler.active_tick = 0
        shared.tick_handler.lost_time = 0
        shared.tick_handler.tick_array.clear()

    async def test_schedule_tick_in_simple(self):
        self.assertEqual(shared.tick_handler.active_tick, 0)

        invoked = 0

        def target():
            nonlocal invoked
            invoked += 1

        shared.tick_handler.bind(target, 2)

        await shared.tick_handler.tick(1 / 20)
        self.assertEqual(invoked, 0)
        self.assertEqual(
            shared.tick_handler.active_tick,
            1,
            (shared.tick_handler.active_tick, shared.tick_handler.lost_time),
        )
        await shared.tick_handler.tick(1 / 20)
        self.assertEqual(invoked, 1)
        self.assertEqual(len(shared.tick_handler.tick_array), 0)
        await shared.tick_handler.tick(1 / 20)
        self.assertEqual(invoked, 1)
        self.assertEqual(len(shared.tick_handler.tick_array), 0)

    async def test_schedule_tick_in_skipping(self):
        self.assertEqual(shared.tick_handler.active_tick, 0)

        invoked = 0

        def target():
            nonlocal invoked
            invoked += 1

        shared.tick_handler.bind(target, 2)

        await shared.tick_handler.tick(4 / 20)
        self.assertEqual(invoked, 1)
        self.assertEqual(len(shared.tick_handler.tick_array), 0)
        await shared.tick_handler.tick(1 / 20)
        self.assertEqual(invoked, 1)
        self.assertEqual(len(shared.tick_handler.tick_array), 0)
