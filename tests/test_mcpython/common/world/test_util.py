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
from tests.util import TestCase


class FakeWorldAccess:
    def __init__(self):
        self.entities = set()
        self.world = {}

    async def add_block(self, position, block):
        self.world[position] = block

    def get_block(self, position):
        return self.world.get(position) if position in self.world else None


class Test(TestCase):
    async def test_fill_area(self):
        from mcpython.common.world.util import fill_area

        world = FakeWorldAccess()

        await fill_area(world, (0, 0, 0), (4, 4, 4), "minecraft:test")

        self.assertEqual(len(world.world), 5 ** 3)
        self.assertTrue(all(v == "minecraft:test" for v in world.world.values()))

    async def test_fill_area_replacing(self):
        from mcpython.common.world.util import fill_area, fill_area_replacing

        world = FakeWorldAccess()

        await fill_area(world, (0, 0, 0), (4, 4, 4), "minecraft:test")
        await fill_area_replacing(
            world, (-1, -1, -1), (6, 25, 2), "minecraft:test2", "minecraft:test"
        )
        self.assertEqual(len(world.world), 5 ** 3)
        # todo: test block count

    # todo: test more
