from unittest import TestCase


class FakeWorldAccess:
    def __init__(self):
        self.world = {}

    def add_block(self, position, block):
        self.world[position] = block

    def get_block(self, position):
        return self.world.get(position) if position in self.world else None


class Test(TestCase):
    def test_fill_area(self):
        from mcpython.common.world.util import fill_area
        world = FakeWorldAccess()

        fill_area(world, (0, 0, 0), (4, 4, 4), "minecraft:test")

        self.assertEqual(len(world.world), 5 ** 3)
        self.assertTrue(all(v == "minecraft:test" for v in world.world.values()))

    def test_fill_area_replacing(self):
        from mcpython.common.world.util import fill_area, fill_area_replacing
        world = FakeWorldAccess()

        fill_area(world, (0, 0, 0), (4, 4, 4), "minecraft:test")
        fill_area_replacing(world, (-1, -1, -1), (6, 25, 2), "minecraft:test2", "minecraft:test")
        self.assertEqual(len(world.world), 5 ** 3)
        # todo: test block count

    # todo: test more
